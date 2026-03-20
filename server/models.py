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


class Expenses(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    __table_args__ = (
        CheckConstraint("length(description) >= 5", name="description_min_length"),
        CheckConstraint("amount > 0", name="positive_amount"),
        CheckConstraint(f"category IN ({', '.join([f'\'{choice}\'' for choice in category_choices])})", name="valid_category")
    )