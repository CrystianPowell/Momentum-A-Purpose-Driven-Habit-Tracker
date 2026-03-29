import tkinter as tk
from tkinter import ttk
from datetime import datetime
import sqlite3
from momentum import get_connection   # <-- Import your DB connection

# -----------------------------
# Task 1.3 — Habit Class
# -----------------------------
class Habit:
    def __init__(self, name, category, why):
        self.name = name
        self.category = category
        self.why = why
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# -----------------------------
# Task 1.4 — Insert Habit into DB
# -----------------------------
def insert_habit_into_db(habit):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO habits (name, category, why, created_at)
        VALUES (?, ?, ?, ?)
    """, (habit.name, habit.category, habit.why, habit.created_at))

    conn.commit()
    conn.close()


# -----------------------------
# Task 1.1 & 1.2 — UI Layout
# -----------------------------
def save_habit():
    name = name_entry.get()
    category = category_var.get()
    why = why_entry.get("1.0", tk.END).strip()

    if not name or not category:
        print("Please fill out all required fields.")
        return

    new_habit = Habit(name, category, why)

    # Task 1.5 — Save to DB
    insert_habit_into_db(new_habit)

    print("Habit saved to database:")
    print("Name:", new_habit.name)
    print("Category:", new_habit.category)
    print("Why:", new_habit.why)
    print("Created at:", new_habit.created_at)
    print("----------------------------------")

    # Clear fields after saving
    name_entry.delete(0, tk.END)
    category_var.set("")
    why_entry.delete("1.0", tk.END)


# Main window
root = tk.Tk()
root.title("Habit Creation")

# Name field
tk.Label(root, text="Habit Name:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
name_entry = tk.Entry(root, width=40)
name_entry.grid(row=0, column=1, padx=10, pady=5)

# Category dropdown
tk.Label(root, text="Category:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
category_var = tk.StringVar()
category_dropdown = ttk.Combobox(root, textvariable=category_var, values=[
    "Health", "Productivity", "Mindset", "Fitness", "Learning", "Other"
], width=37)
category_dropdown.grid(row=1, column=1, padx=10, pady=5)

# Why field
tk.Label(root, text="Why this habit?").grid(row=2, column=0, sticky="nw", padx=10, pady=5)
why_entry = tk.Text(root, width=30, height=5)
why_entry.grid(row=2, column=1, padx=10, pady=5)

# Save button
save_button = tk.Button(root, text="Save Habit", command=save_habit)
save_button.grid(row=3, column=1, pady=10)

root.mainloop()
