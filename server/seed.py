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
    users = [user1, user2]
    descriptions = [
        "Lunch at cafe", "Bus ticket", "Movie night", "Electricity bill", "Groceries",
        "Taxi ride", "Concert ticket", "Water bill", "Snacks", "Gym membership"
    ]
    for user in users:
        for i in range(10):
            expense = Expenses(
                amount=round(random.uniform(5, 100), 2),
                description=descriptions[i % len(descriptions)],
                category=random.choice(category_choices),
                user_id=user.id
            )
            db.session.add(expense)
    db.session.commit()
    print("Seeded 10 expenses per user.")
    