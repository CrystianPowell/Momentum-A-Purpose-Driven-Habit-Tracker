"""
Momentum – Streak Engine & Grace Day Logic
Tasks 4.1, 4.2, 4.3
"""

from datetime import datetime, timedelta
from momentum import get_connection


# -----------------------------
# Task 4.1 — Streak Calculation
# -----------------------------
def calculate_streak(habit_id):
    """
    Count consecutive completed days ending at today (or yesterday).
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT date FROM checkins
        WHERE habit_id = ? AND completed = 1
        ORDER BY date DESC
    """, (habit_id,))

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return 0

    streak = 0
    today = datetime.now().date()
    check_dates = set(row[0] for row in rows)

    current_day = today
    if str(current_day) not in check_dates:
        current_day = today - timedelta(days=1)

    while str(current_day) in check_dates:
        streak += 1
        current_day -= timedelta(days=1)

    return streak


# -----------------------------------
# Task 4.2 — Grace Day Initialization
# -----------------------------------
def initialize_grace_days(habit_id, count=2):
    """Give a new habit 2 grace days (skip-without-breaking-streak passes)."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM grace_days WHERE habit_id = ?", (habit_id,))

    if cursor.fetchone() is None:
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("""
            INSERT INTO grace_days (habit_id, remaining, reset_date)
            VALUES (?, ?, ?)
        """, (habit_id, count, today))

    conn.commit()
    conn.close()


def get_grace_days_remaining(habit_id):
    """Return how many grace days a habit has left."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT remaining FROM grace_days WHERE habit_id = ?", (habit_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 0


# -----------------------------
# Task 4.3 — Use a Grace Day
# -----------------------------
def use_grace_day(habit_id):
    """Consume one grace day. Returns True if used, False if none remain."""
    remaining = get_grace_days_remaining(habit_id)

    if remaining <= 0:
        return False

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE grace_days
        SET remaining = remaining - 1
        WHERE habit_id = ?
    """, (habit_id,))
    conn.commit()
    conn.close()
    return True
