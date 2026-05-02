import tkinter as tk
from tkinter import ttk, messagebox
from momentum import get_connection
from datetime import datetime

def load_habits():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, category FROM habits ORDER BY created_at DESC")
    habits = cursor.fetchall()
    conn.close()
    return habits

def update_habit(habit_id, new_name, new_category):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE habits
        SET name = ?, category = ?
        WHERE id = ?
    """, (new_name, new_category, habit_id))
    conn.commit()
    conn.close()

def build_edit_habit():
    root = tk.Tk()
    root.title("Edit Habit")

    tk.Label(root, text="Select Habit:").grid(row=0, column=0, padx=10, pady=5)

    habits = load_habits()
    habit_names = [h[1] for h in habits]

    habit_var = tk.StringVar()
    habit_dropdown = ttk.Combobox(root, textvariable=habit_var, values=habit_names, width=40)
    habit_dropdown.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(root, text="New Name:").grid(row=1, column=0, padx=10, pady=5)
    name_entry = tk.Entry(root, width=42)
    name_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(root, text="New Category:").grid(row=2, column=0, padx=10, pady=5)
    category_entry = tk.Entry(root, width=42)
    category_entry.grid(row=2, column=1, padx=10, pady=5)

    def load_selected():
        selected = habit_var.get()
        if not selected:
            return

        for h in habits:
            if h[1] == selected:
                habit_id, name, category = h
                name_entry.delete(0, tk.END)
                name_entry.insert(0, name)
                category_entry.delete(0, tk.END)
                category_entry.insert(0, category)
                break

    def save_changes():
        selected = habit_var.get()
        if not selected:
            messagebox.showinfo("Edit Habit", "Please select a habit.")
            return

        new_name = name_entry.get().strip()
        new_category = category_entry.get().strip()

        if not new_name or not new_category:
            messagebox.showinfo("Edit Habit", "Name and category cannot be empty.")
            return

        habit_id = None
        for h in habits:
            if h[1] == selected:
                habit_id = h[0]
                break

        update_habit(habit_id, new_name, new_category)
        messagebox.showinfo("Edit Habit", "Habit updated successfully!")

    tk.Button(root, text="Load Habit", command=load_selected).grid(row=3, column=0, pady=10)
    tk.Button(root, text="Save Changes", command=save_changes).grid(row=3, column=1, pady=10)

    root.mainloop()

if __name__ == "__main__":
    build_edit_habit()
