from faker import Faker
from datetime import datetime
import random
from werkzeug.security import generate_password_hash

from app import app
from db import get_db
from models.user import User
from models.transaction import Transaction

fake = Faker()

# Predefined test users
test_users = [
    {"email": "ra@ra.com", "password": "ra123", "username": "Raed"},
    {"email": "ice@ice.com", "password": "ice123", "username": "Ice"},
    {"email": "su@su.com", "password": "su123", "username": "Su"},
    {"email": "jeff@jeff.com", "password": "jeff123", "username": "Jeff"},
]

def create_transactions_for_user(db, user, num=1000):
    categories = [
        "Groceries", "Utilities", "Entertainment", "Transport", "Dining",
        "Healthcare", "Rent", "Insurance", "Subscriptions", "Travel", "Education"
    ]
    for _ in range(num):
        txn = Transaction(
            user_id=user.id,
            amount=round(random.uniform(5, 500), 2),
            type=random.choice(["debit", "credit"]),
            category=random.choice(categories),
            description=fake.sentence(nb_words=4),
            date=fake.date_between(start_date="-180d", end_date="today"),
            time=fake.time_object(),  # Must be a Python time object
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(txn)
    db.commit()

def seed():
    db = get_db()

    print("\n🧪 Seeding test users and transactions...\n")

    for u in test_users:
        # Delete existing user (and their transactions) by email
        existing = db.query(User).filter_by(email=u["email"]).first()
        if existing:
            db.query(Transaction).filter_by(user_id=existing.id).delete()
            db.delete(existing)
            db.commit()

        # Add fresh user
        user = User(
            email=u["email"],
            username=u["username"],
            password=generate_password_hash(u["password"]),
            created_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()

        create_transactions_for_user(db, user)
        print(f"👤 {u['username']} | 📧 {u['email']} | 🔑 {u['password']}")

    print("\n✅ Seeding complete!\n")
    print("🔐 test_users = [")
    for u in test_users:
        print(f"    {{\"email\": \"{u['email']}\", \"password\": \"{u['password']}\", \"username\": \"{u['username']}\"}},")
    print("]")
    print()

if __name__ == "__main__":
    with app.app_context():
        seed()
