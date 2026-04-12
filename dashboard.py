import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from momentum import get_connection
import subprocess
import sys
from datetime import datetime

def get_habits():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, category, created_at
        FROM habits
        ORDER BY created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_today_status(habit_id):
    conn = get_connection()
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
        SELECT completed
        FROM checkins
        WHERE habit_id = ? AND date = ?
    """, (habit_id, today))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return "No Check-in"
    return "Done" if row[0] == 1 else "Missed"

def delete_habit(habit_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM checkins WHERE habit_id = ?", (habit_id,))
    cursor.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
    conn.commit()
    conn.close()

def open_progress_summary():
    # Run progress_summary.py as a separate process
    subprocess.Popen([sys.executable, "progress_summary.py"])

def open_habit_creation():
    subprocess.Popen([sys.executable, "habit_creation.py"])

def open_daily_checkin():
    subprocess.Popen([sys.executable, "daily_checkin.py"])

def build_dashboard():
    root = tk.Tk()
    root.title("Momentum Dashboard")

    top_frame = tk.Frame(root)
    top_frame.pack(fill="x", padx=10, pady=10)

    tk.Button(top_frame, text="New Habit", command=open_habit_creation).pack(side="left", padx=5)
    tk.Button(top_frame, text="Daily Check-In", command=open_daily_checkin).pack(side="left", padx=5)
    tk.Button(top_frame, text="View Progress", command=open_progress_summary).pack(side="left", padx=5)

    columns = ("name", "category", "created_at", "status")
    tree = ttk.Treeview(root, columns=columns, show="headings", height=10)
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    tree.heading("name", text="Habit")
    tree.heading("category", text="Category")
    tree.heading("created_at", text="Created At")
    tree.heading("status", text="Today Status")

    tree.column("name", width=180)
    tree.column("category", width=120)
    tree.column("created_at", width=140)
    tree.column("status", width=120)

    habits = get_habits()
    for habit in habits:
        habit_id, name, category, created_at = habit
        status = get_today_status(habit_id)
        tree.insert("", "end", iid=str(habit_id), values=(name, category, created_at, status))

    # Color rows based on status
    def color_rows():
        for item in tree.get_children():
            status = tree.item(item, "values")[3]
            if status == "Done":
                tree.tag_configure("done", background="#d4f8d4")
                tree.item(item, tags=("done",))
            elif status == "Missed":
                tree.tag_configure("missed", background="#f8d4d4")
                tree.item(item, tags=("missed",))
            else:
                tree.tag_configure("none", background="#ffffff")
                tree.item(item, tags=("none",))

    color_rows()

    # Delete button
    def on_delete():
        selected = tree.selection()
        if not selected:
            messagebox.showinfo("Delete Habit", "Please select a habit to delete.")
            return
        habit_id = int(selected[0])
        confirm = messagebox.askyesno("Delete Habit", "Are you sure you want to delete this habit and its check-ins?")
        if confirm:
            delete_habit(habit_id)
            tree.delete(selected[0])

    bottom_frame = tk.Frame(root)
    bottom_frame.pack(fill="x", padx=10, pady=10)

    tk.Button(bottom_frame, text="Delete Habit", command=on_delete).pack(side="right")

    root.mainloop()

if __name__ == "__main__":
    build_dashboard()

'''"""
Momentum – Dashboard / Habit List View
Tasks 2.1, 2.2, 2.3
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from momentum import get_connection
from streak_engine import calculate_streak, get_grace_days_remaining


# -----------------------------------------
# Task 2.2 — Load Habits from the Database
# -----------------------------------------
def load_habits():
    """Fetch all habits from the database and return as a list of tuples."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, category, why, created_at
        FROM habits
        ORDER BY created_at DESC
    """)
    habits = cursor.fetchall()
    conn.close()
    return habits


# -------------------------------------------
# Task 2.3 — Delete a Habit (with cascading)
# -------------------------------------------
def delete_habit(habit_id):
    """Delete a habit and its related check-ins and grace days."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM checkins WHERE habit_id = ?", (habit_id,))
    cursor.execute("DELETE FROM grace_days WHERE habit_id = ?", (habit_id,))
    cursor.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
    conn.commit()
    conn.close()


# -----------------------------------------------
# Task 2.1, 2.2, 2.3 — Dashboard UI (Tkinter)
# -----------------------------------------------
def open_dashboard(root=None, on_navigate_create=None, on_navigate_checkin=None):
    """
    Build and display the Dashboard screen.
    Shows all habits with current streaks and grace-day counts.
    Provides buttons to navigate to Habit Creation and Daily Check-In.
    """
    is_standalone = root is None
    if is_standalone:
        root = tk.Tk()

    root.title("Momentum — Dashboard")
    root.geometry("750x480")

    # --- Header ---
    header = tk.Frame(root)
    header.pack(fill="x", padx=15, pady=(15, 5))

    tk.Label(
        header, text="My Habits", font=("Helvetica", 18, "bold")
    ).pack(side="left")

    btn_frame = tk.Frame(header)
    btn_frame.pack(side="right")

    if on_navigate_create:
        tk.Button(
            btn_frame, text="+ New Habit", command=on_navigate_create
        ).pack(side="left", padx=5)

    if on_navigate_checkin:
        tk.Button(
            btn_frame, text="Daily Check-In", command=on_navigate_checkin
        ).pack(side="left", padx=5)

    # --- Habit Table (Treeview) ---
    columns = ("name", "category", "streak", "grace", "created")
    tree = ttk.Treeview(root, columns=columns, show="headings", height=12)

    tree.heading("name", text="Habit")
    tree.heading("category", text="Category")
    tree.heading("streak", text="Streak 🔥")
    tree.heading("grace", text="Grace Days")
    tree.heading("created", text="Created")

    tree.column("name", width=180)
    tree.column("category", width=110)
    tree.column("streak", width=85, anchor="center")
    tree.column("grace", width=95, anchor="center")
    tree.column("created", width=130)

    tree.pack(fill="both", expand=True, padx=15, pady=5)

    scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    # --- Populate Table ---
    def refresh_table():
        tree.delete(*tree.get_children())
        habits = load_habits()

        for habit in habits:
            h_id, name, category, why, created_at = habit
            streak = calculate_streak(h_id)
            grace = get_grace_days_remaining(h_id)
            tree.insert("", "end", iid=h_id, values=(
                name,
                category,
                f"{streak} day{'s' if streak != 1 else ''}",
                f"{grace} left",
                created_at[:10]
            ))

        if not habits:
            tree.insert("", "end", values=(
                "No habits yet!", "—", "—", "—", "—"
            ))

    refresh_table()

    # --- Detail / Action Panel ---
    detail_frame = tk.Frame(root)
    detail_frame.pack(fill="x", padx=15, pady=(0, 10))

    why_label = tk.Label(
        detail_frame, text="Select a habit to see your 'why'.",
        wraplength=500, justify="left", fg="#555"
    )
    why_label.pack(side="left", fill="x", expand=True)

    def on_select(event):
        selected = tree.selection()
        if not selected:
            return
        h_id = int(selected[0])
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT why FROM habits WHERE id = ?", (h_id,))
        row = cursor.fetchone()
        conn.close()
        if row and row[0]:
            why_label.config(text=f'Why: "{row[0]}"')
        else:
            why_label.config(text="No 'why' recorded for this habit.")

    tree.bind("<<TreeviewSelect>>", on_select)

    def on_delete():
        selected = tree.selection()
        if not selected:
            messagebox.showinfo("Delete", "Select a habit first.")
            return
        h_id = int(selected[0])
        confirm = messagebox.askyesno(
            "Delete Habit",
            "Are you sure? This will remove the habit and all its check-ins."
        )
        if confirm:
            delete_habit(h_id)
            refresh_table()
            why_label.config(text="Habit deleted.")

    tk.Button(
        detail_frame, text="Delete Selected", fg="red", command=on_delete
    ).pack(side="right")

    if is_standalone:
        root.mainloop()

    return refresh_table


if __name__ == "__main__":
    open_dashboard()
'''
