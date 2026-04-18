import tkinter as tk
from tkinter import ttk
import sqlite3
from momentum import get_connection
import matplotlib.pyplot as plt
from datetime import datetime

def load_habits():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM habits ORDER BY name ASC")
    habits = cursor.fetchall()
    conn.close()
    return habits

def load_history(habit_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT date, completed
        FROM checkins
        WHERE habit_id = ?
        ORDER BY date ASC
    """, (habit_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def show_chart(history, habit_name):
    if not history:
        return

    dates = [datetime.strptime(row[0], "%Y-%m-%d") for row in history]
    values = [row[1] for row in history]

    plt.figure(figsize=(8, 4))
    plt.plot(dates, values, marker="o", linestyle="-", color="blue")
    plt.title(f"Streak History for {habit_name}")
    plt.xlabel("Date")
    plt.ylabel("Completed (1 = Yes, 0 = No)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def build_ui():
    root = tk.Tk()
    root.title("Habit History")

    tk.Label(root, text="Select Habit:").grid(row=0, column=0, padx=10, pady=5)

    habit_var = tk.StringVar()
    habit_dropdown = ttk.Combobox(root, textvariable=habit_var, width=40)
    habit_dropdown.grid(row=0, column=1, padx=10, pady=5)

    habits = load_habits()
    habit_dropdown["values"] = [h[1] for h in habits]

    columns = ("date", "completed")
    tree = ttk.Treeview(root, columns=columns, show="headings", height=12)
    tree.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

    tree.heading("date", text="Date")
    tree.heading("completed", text="Completed")

    def load_selected_habit():
        habit_name = habit_var.get()
        if not habit_name:
            return

        habit_id = [h[0] for h in habits if h[1] == habit_name][0]
        history = load_history(habit_id)

        for row in tree.get_children():
            tree.delete(row)

        for date, completed in history:
            status = "Yes" if completed == 1 else "No"
            tree.insert("", "end", values=(date, status))

    def open_chart():
        habit_name = habit_var.get()
        if not habit_name:
            return

        habit_id = [h[0] for h in habits if h[1] == habit_name][0]
        history = load_history(habit_id)
        show_chart(history, habit_name)

    tk.Button(root, text="Load History", command=load_selected_habit).grid(row=2, column=0, pady=10)
    tk.Button(root, text="View Chart", command=open_chart).grid(row=2, column=1, pady=10)

    root.mainloop()

if __name__ == "__main__":
    build_ui()
