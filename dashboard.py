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

