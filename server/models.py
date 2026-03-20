from sqlalchemy import CheckConstraint
from sqlalchemy.orm import validates as model_validates
from sqlalchemy.ext.hybrid import hybrid_property
from marshmallow import Schema, fields, validates_schema, ValidationError

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
        CheckConstraint("length(username) >= 5", name="username_min_length"),
    )

    @model_validates('username')
    def validate_username(self, key, value):
        if not isinstance(value, str):
            raise ValueError(f"{key} must be a string.")
        if len(value) < 5:
            raise ValueError(f"{key} must be at least 5 characters long.")
        if User.query.filter_by(username=value).first():
            raise ValueError(f"{key} must be unique.")        
        return value
    
    expenses = db.relationship('Expenses', back_populates='user', cascade='all, delete-orphan')


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