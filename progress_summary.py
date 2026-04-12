import tkinter as tk
from tkinter import ttk
import sqlite3
from momentum import get_connection

def calculate_stats():
    conn = get_connection()
    cursor = conn.cursor()

    # Total habits
    cursor.execute("SELECT COUNT(*) FROM habits")
    total_habits = cursor.fetchone()[0]

    # Total check-ins and completed check-ins
    cursor.execute("SELECT COUNT(*), SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END) FROM checkins")
    row = cursor.fetchone()
    total_checkins = row[0] if row[0] is not None else 0
    completed_checkins = row[1] if row[1] is not None else 0

    # Completion rate
    completion_rate = 0
    if total_checkins > 0:
        completion_rate = int((completed_checkins / total_checkins) * 100)

    # Average streak length per habit (simple version)
    cursor.execute("SELECT id FROM habits")
    habit_ids = [r[0] for r in cursor.fetchall()]

    def calculate_streak(habit_id):
        cursor.execute("""
            SELECT date, completed
            FROM checkins
            WHERE habit_id = ?
            ORDER BY date DESC
        """, (habit_id,))
        rows = cursor.fetchall()
        streak = 0
        last_date = None
        for date_str, completed in rows:
            if completed != 1:
                break
            streak += 1
        return streak

    streaks = [calculate_streak(hid) for hid in habit_ids] if habit_ids else []
    avg_streak = int(sum(streaks) / len(streaks)) if streaks else 0

    conn.close()
    return total_habits, total_checkins, completion_rate, avg_streak

def build_ui():
    total_habits, total_checkins, completion_rate, avg_streak = calculate_stats()

    root = tk.Tk()
    root.title("Progress Summary")

    tk.Label(root, text="Progress Summary", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

    tk.Label(root, text="Total Habits:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
    tk.Label(root, text=str(total_habits)).grid(row=1, column=1, sticky="w", padx=10, pady=5)

    tk.Label(root, text="Total Check-ins:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
    tk.Label(root, text=str(total_checkins)).grid(row=2, column=1, sticky="w", padx=10, pady=5)

    tk.Label(root, text="Completion Rate:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
    rate_frame = tk.Frame(root)
    rate_frame.grid(row=3, column=1, sticky="w", padx=10, pady=5)
    rate_bar = ttk.Progressbar(rate_frame, length=200, maximum=100)
    rate_bar["value"] = completion_rate
    rate_bar.pack(side="left")
    tk.Label(rate_frame, text=f"{completion_rate}%").pack(side="left", padx=5)

    tk.Label(root, text="Average Streak Length:").grid(row=4, column=0, sticky="w", padx=10, pady=5)
    tk.Label(root, text=f"{avg_streak} days").grid(row=4, column=1, sticky="w", padx=10, pady=5)

    root.mainloop()

if __name__ == "__main__":
    build_ui()
