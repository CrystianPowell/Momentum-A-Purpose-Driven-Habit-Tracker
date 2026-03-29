import tkinter as tk
from tkinter import ttk
from datetime import datetime

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
    print("Habit created:")
    print("Name:", new_habit.name)
    print("Category:", new_habit.category)
    print("Why:", new_habit.why)
    print("Created at:", new_habit.created_at)
    print("----------------------------------")


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
