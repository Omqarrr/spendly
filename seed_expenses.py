import random
import sys
import os
from datetime import datetime, timedelta

# Add database path to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'database'))

from db import get_db

user_id = 2
count = 5
months = 3

# Verify user exists
conn = get_db()
user = conn.execute('SELECT id FROM users WHERE id = ?', (user_id,)).fetchone()
if not user:
    print(f"No user found with id {user_id}.")
    sys.exit(1)

# Categories with realistic Indian descriptions and amounts
expense_templates = {
    'Food': [
        ('Street food at local stall', 50, 300),
        ('Monthly groceries from market', 400, 800),
        ('Restaurant dinner', 200, 600),
        ('Tea/coffee at dhaba', 30, 100),
        ('Birthday party thali', 300, 500),
    ],
    'Transport': [
        ('Bus ticket', 20, 50),
        ('Auto-rickshaw ride', 40, 150),
        ('Petrol refill', 200, 500),
        ('Train ticket', 100, 300),
        ('Metro pass', 50, 150),
    ],
    'Bills': [
        ('Electricity bill', 300, 800),
        ('Mobile recharge', 200, 400),
        ('Internet bill', 400, 1000),
        ('Gas cylinder', 500, 1200),
        ('Water bill', 150, 300),
    ],
    'Health': [
        ('Pharmacy medicines', 100, 400),
        ('Doctor consultation', 300, 800),
        ('Dental checkup', 500, 1200),
        ('Blood test', 400, 700),
        ('First aid supplies', 200, 500),
    ],
    'Entertainment': [
        ('Cinema tickets', 200, 500),
        ('Streaming subscription', 300, 600),
        ('Gaming voucher', 200, 800),
        ('Concert entry', 500, 1500),
        ('Sports event', 400, 1000),
    ],
    'Shopping': [
        ('Clothing purchase', 500, 2000),
        ('Electronics accessory', 800, 3000),
        ('Home decor item', 300, 1500),
        ('Book purchase', 200, 800),
        ('Festival shopping', 1000, 5000),
    ],
    'Other': [
        ('Charity donation', 50, 300),
        ('Gift purchase', 100, 500),
        ('Emergency repair', 200, 800),
        ('Bank charges', 50, 200),
        ('Miscellaneous', 50, 400),
    ],
}

# Category weights (Food most common, Health/Entertainment least)
category_weights = {
    'Food': 35,
    'Transport': 20,
    'Bills': 15,
    'Health': 8,
    'Entertainment': 10,
    'Shopping': 10,
    'Other': 2,
}

# Generate random date within past months
def random_date(months_back):
    today = datetime.now()
    start = today - timedelta(days=months_back * 30)
    random_days = random.randint(0, months_back * 30)
    return start + timedelta(days=random_days)

# Generate expenses
expenses_to_insert = []
for _ in range(count):
    cat = random.choices(list(category_weights.keys()), weights=list(category_weights.values()))[0]
    desc, min_amt, max_amt = random.choice(expense_templates[cat])
    amount = round(random.uniform(min_amt, max_amt), 2)
    date = random_date(months).strftime('%Y-%m-%d')
    expenses_to_insert.append((user_id, amount, cat, date, desc))

# Insert all expenses in a single transaction
try:
    cursor = conn.cursor()
    cursor.executemany('''
        INSERT INTO expenses (user_id, amount, category, date, description)
        VALUES (?, ?, ?, ?, ?)
    ''', expenses_to_insert)
    conn.commit()
    inserted_count = cursor.rowcount
    
    # Get date range
    dates = [e[3] for e in expenses_to_insert]
    min_date = min(dates)
    max_date = max(dates)
    
    # Get inserted records with IDs
    for expense in expenses_to_insert[:5]:
        expense_id = cursor.lastrowid - len(expenses_to_insert) + expenses_to_insert.index(expense)
        # Actually fetch from DB to get proper IDs
    conn.close()
    
    # Fetch the inserted records
    conn = get_db()
    sample = conn.execute('''
        SELECT id, user_id, amount, category, date, description 
        FROM expenses 
        WHERE date BETWEEN ? AND ? AND user_id = ?
        ORDER BY id DESC LIMIT 5
    ''', (min_date, max_date, user_id)).fetchall()
    conn.close()
    
    print(f"Inserted {inserted_count} expenses")
    print(f"Date range: {min_date} to {max_date}")
    print("\nSample of 5 inserted records:")
    for row in sample:
        print(f"  - id: {row['id']}, amount: ₹{row['amount']}, category: {row['category']}, date: {row['date']}, description: {row['description']}")
    
except Exception as e:
    conn.rollback()
    print(f"Error: {e}")
    sys.exit(1)
