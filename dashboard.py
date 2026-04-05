"""
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
