#!/usr/bin/env python3

from app import app
from models import db, User, Expenses, category_choices

import random

with app.app_context():
    print("Deleting existing data...")
    db.session.query(Expenses).delete()
    db.session.query(User).delete()
    db.session.commit()

    print("Seeding users...")
    user1 = User(username="alice")
    user1.password_hash = "password1"
    user2 = User(username="bob")
    user2.password_hash = "password2"
    db.session.add_all([user1, user2])
    db.session.commit()

    print("Seeding expenses...")
    # Expenses for user1 (alice)
    e1 = Expenses(amount=12.50, description="Lunch at cafe", category="Food", user=user1)
    e2 = Expenses(amount=25.00, description="Gas refill", category="Transportation", user=user1)
    e3 = Expenses(amount=15.99, description="Movie ticket", category="Entertainment", user=user1)
    e4 = Expenses(amount=60.00, description="Electric bill", category="Utilities", user=user1)
    e5 = Expenses(amount=45.20, description="Groceries trip", category="Food", user=user1)
    e6 = Expenses(amount=10.00, description="Bus ticket", category="Transportation", user=user1)
    e7 = Expenses(amount=8.99, description="Spotify plan", category="Entertainment", user=user1)
    e8 = Expenses(amount=30.00, description="Dinner out", category="Food", user=user1)
    e9 = Expenses(amount=22.75, description="Online order", category="Other", user=user1)
    e10 = Expenses(amount=18.40, description="Snacks store", category="Food", user=user1)

    # Expenses for user2 (bob)
    e11 = Expenses(amount=14.00, description="Lunch combo", category="Food", user=user2)
    e12 = Expenses(amount=50.00, description="Uber ride", category="Transportation", user=user2)
    e13 = Expenses(amount=20.00, description="Cinema ticket", category="Entertainment", user=user2)
    e14 = Expenses(amount=75.00, description="Water bill", category="Utilities", user=user2)
    e15 = Expenses(amount=90.00, description="Supermarket run", category="Food", user=user2)
    e16 = Expenses(amount=12.00, description="Train ticket", category="Transportation", user=user2)
    e17 = Expenses(amount=9.99, description="Netflix plan", category="Entertainment", user=user2)
    e18 = Expenses(amount=40.00, description="Dinner date", category="Food", user=user2)
    e19 = Expenses(amount=27.50, description="Amazon order", category="Other", user=user2)
    e20 = Expenses(amount=16.80, description="Coffee shop", category="Food", user=user2)

    db.session.add_all([
        e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
        e11, e12, e13, e14, e15, e16, e17, e18, e19, e20
    ])

    db.session.commit()
    
    db.session.commit()
    print("Seeded 10 expenses per user.")
    