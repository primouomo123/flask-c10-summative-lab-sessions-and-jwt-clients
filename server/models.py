from sqlalchemy import CheckConstraint
from sqlalchemy.orm import validates as model_validates
from sqlalchemy.ext.hybrid import hybrid_property
from marshmallow import Schema, fields, validate, validates as schema_validates, ValidationError, RAISE, post_load

from config import db, bcrypt

category_choices = ['Food', 'Transportation', 'Entertainment', 'Utilities', 'Other']

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    _password_hash = db.Column(db.String(128), nullable=True)

    @hybrid_property
    def password_hash(self):
        raise AttributeError("Password hashes may not be viewed.")
    
    @password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(password.encode('utf-8'))
        self._password_hash = password_hash.decode('utf-8')
    
    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))
    
    __table_args__ = (
        CheckConstraint("length(username) >= 3", name="username_min_length"),
    )

    @model_validates('username')
    def validate_username(self, key, value):
        if not isinstance(value, str):
            raise ValueError(f"{key} must be a string.")
        if len(value) < 3:
            raise ValueError(f"{key} must be at least 3 characters long.")
        if User.query.filter_by(username=value).first():
            raise ValueError(f"{key} must be unique.")        
        return value
    
    expenses = db.relationship('Expenses', back_populates='user', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<User id={self.id} username={self.username}>"

class Expenses(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    __table_args__ = (
        CheckConstraint("length(description) >= 5", name="description_min_length"),
        CheckConstraint("amount > 0", name="positive_amount"),
        CheckConstraint(f"category IN ({', '.join([f'\'{choice}\'' for choice in category_choices])})", name="valid_category")
    )

    @model_validates('amount')
    def validate_amount(self, key, value):
        if not isinstance(value, (int, float)):
            raise ValueError(f"{key} must be a number.")
        if value <= 0:
            raise ValueError(f"{key} must be greater than 0.")        
        return value

    @model_validates('description')
    def validate_description(self, key, value):
        if not isinstance(value, str):
            raise ValueError(f"{key} must be a string.")
        if len(value) < 5:
            raise ValueError(f"{key} must be at least 5 characters long.")        
        return value
    
    @model_validates('category')
    def validate_category(self, key, value):
        if not isinstance(value, str):
            raise ValueError(f"{key} must be a string.")
        if value not in category_choices:
            raise ValueError(f"{key} must be one of {category_choices}.")        
        return value
    
    user = db.relationship('User', back_populates='expenses')

    def __repr__(self):
        return f"<Expenses id={self.id} amount={self.amount} description={self.description} category={self.category} user_id={self.user_id}>"


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    password_hash = fields.Str(load_only=True, required=True, validate=validate.Length(equal=128))

    expenses = fields.Method("get_expenses", dump_only=True)

    def get_expenses(self, obj):
        # Get optional limit from context
        limit = self.context.get("limit")

        expenses = obj.expenses

        if limit is not None:
            expenses = expenses[:limit]

        return ExpensesSchema(
            many=True,
            exclude=('user',)
        ).dump(expenses)

    class Meta:
        unknown = RAISE
        ordered = True
    
    @schema_validates('username')
    def validate_unique_username(self, value, **kwargs):
        if not isinstance(value, str):
            raise ValidationError("Username must be a string.", field_name='username')
        if len(value) < 3 or len(value) > 50:
            raise ValidationError("Username must be between 3 and 50 characters long.", field_name='username')
        if User.query.filter_by(username=value).first():
            raise ValidationError("Username must be unique.", field_name='username')
        return value
    
    @post_load
    def create_user(self, data, **kwargs):
        user = User(username=data['username'])
        user.password_hash = data['password_hash']
        return user
            

class ExpensesSchema(Schema):
    id = fields.Int(dump_only=True)
    amount = fields.Float(required=True, validate=validate.Range(min=0.01))
    description = fields.Str(required=True, validate=validate.Length(min=5, max=255))
    category = fields.Str(required=True, validate=validate.OneOf(category_choices))
    user_id = fields.Int(load_only=True, required=True)

    user = fields.Nested(UserSchema(exclude=('expenses',)), dump_only=True)

    class Meta:
        unknown = RAISE
        ordered = True
    
    @schema_validates('amount')
    def validate_amount(self, value, **kwargs):
        if not isinstance(value, float):
            raise ValidationError("Amount must be a number.", field_name='amount')
        if value <= 0:
            raise ValidationError("Amount must be greater than 0.", field_name='amount')
        return value
    
    @schema_validates('description')
    def validate_description(self, value, **kwargs):
        if not isinstance(value, str):
            raise ValidationError("Description must be a string.", field_name='description')
        if len(value) < 5 or len(value) > 255:
            raise ValidationError("Description must be between 5 and 255 characters long.", field_name='description')
        return value
    
    @schema_validates('category')
    def validate_category(self, value, **kwargs):
        if not isinstance(value, str):
            raise ValidationError("Category must be a string.", field_name='category')
        if value not in category_choices:
            raise ValidationError(f"Category must be one of {category_choices}.", field_name='category')
        return value
    
    @schema_validates('user_id')
    def validate_user_exists(self, value, **kwargs):
        if not isinstance(value, int):
            raise ValidationError("User ID must be an integer.", field_name='user_id')
        if value <= 0:
            raise ValidationError("User ID must be a positive integer.", field_name='user_id')
        if not User.query.get(value):
            raise ValidationError("User with given ID does not exist.", field_name='user_id')
    
    @post_load
    def create_expense(self, data, **kwargs):
        return Expenses(**data)