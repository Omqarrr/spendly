import sqlite3
from werkzeug.security import generate_password_hash
import os


def get_db():
    """Returns a SQLite connection with row_factory and foreign keys enabled"""
    # Get the project root directory (parent of database directory)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(project_root, 'spendly.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def init_db():
    """Creates all tables using CREATE TABLE IF NOT EXISTS"""
    conn = get_db()
    try:
        # Create users table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Create expenses table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        conn.commit()
    finally:
        conn.close()


def seed_db():
    """Inserts sample data for development"""
    conn = get_db()
    try:
        # Check if users table already has data
        cursor = conn.execute('SELECT COUNT(*) FROM users')
        if cursor.fetchone()[0] > 0:
            return  # Data already seeded
        # Insert demo user
        demo_password_hash = generate_password_hash('demo123')
        conn.execute('''
            INSERT INTO users (name, email, password_hash)
            VALUES (?, ?, ?)
        ''', ('Demo User', 'demo@spendly.com', demo_password_hash))
        user_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        # Insert sample expenses
        sample_expenses = [
            (user_id, 15.50, 'Food', '2026-06-01', 'Groceries at supermarket'),
            (user_id, 12.75, 'Food', '2026-06-10', 'Lunch at cafe'),
            (user_id, 45.00, 'Food', '2026-06-20', 'Dinner at restaurant'),
            (user_id, 60.00, 'Transport', '2026-06-05', 'Monthly bus pass'),
            (user_id, 35.00, 'Transport', '2026-06-18', 'Gas refill'),
            (user_id, 120.00, 'Bills', '2026-06-01', 'Electricity bill'),
            (user_id, 25.00, 'Health', '2026-06-12', 'Pharmacy purchase'),
            (user_id, 30.00, 'Entertainment', '2026-06-15', 'Movie tickets'),
            (user_id, 80.00, 'Shopping', '2026-06-22', 'New clothes'),
            (user_id, 20.00, 'Other', '2026-06-25', 'Miscellaneous')
        ]
        conn.executemany('''
            INSERT INTO expenses (user_id, amount, category, date, description)
            VALUES (?, ?, ?, ?, ?)
        ''', sample_expenses)
        conn.commit()
    finally:
        conn.close()


def get_user_by_email(email):
    """Return user row dict or None for given email"""
    conn = get_db()
    try:
        cur = conn.execute('SELECT * FROM users WHERE email = ?', (email,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def register_user(name, email, password):
    """Register a new user. Returns the new user's ID.

    Raises:
        ValueError: If the email already exists or validation fails.
    """
    conn = get_db()
    hashed_pw = generate_password_hash(password)
    try:
        result = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, hashed_pw)
        )
        conn.commit()
        return result.lastrowid
    except sqlite3.IntegrityError:
        conn.rollback()
        raise ValueError("Email already registered")
    finally:
        conn.close()