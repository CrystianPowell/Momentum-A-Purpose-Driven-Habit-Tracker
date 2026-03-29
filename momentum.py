import os
import sqlite3
from datetime import datetime

DB_NAME = "momentum.db"

def database_exists():
    return os.path.exists(DB_NAME)

def get_connection():
    return sqlite3.connect(DB_NAME)

def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    # Habits table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            why TEXT,
            created_at TEXT NOT NULL
        )
    """)

    # Daily check-ins table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS checkins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            completed INTEGER NOT NULL,
            FOREIGN KEY (habit_id) REFERENCES habits(id)
        )
    """)

    # Weekly reflections table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reflections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            text TEXT NOT NULL
        )
    """)

    # Grace days table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS grace_days (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            remaining INTEGER NOT NULL,
            reset_date TEXT NOT NULL,
            FOREIGN KEY (habit_id) REFERENCES habits(id)
        )
    """)

    conn.commit()
    conn.close()

def main():
    print("Starting Momentum...")

    # Task 6.1 — Detect first launch
    if not database_exists():
        print("First launch detected. Creating database...")
        initialize_database()
        print("Database created successfully.")
    else:
        print("Database already exists. Skipping initialization.")

    print("Setup complete. You can now build Feature 1.")

if __name__ == "__main__":
    main()
