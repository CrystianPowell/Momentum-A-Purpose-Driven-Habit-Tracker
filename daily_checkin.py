"""
Momentum – Daily Check-In Screen
Tasks 3.1, 3.2, 3.3
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from momentum import get_connection
from streak_engine import (
    calculate_streak,
    get_grace_days_remaining,
    use_grace_day,
    initialize_grace_days,
)


# -----------------------------------------------
# Task 3.2 — Record a Check-In in the Database
# -----------------------------------------------
def record_checkin(habit_id, completed):
    """
    Insert a check-in row for today.
    completed: 1 = done, 0 = missed.
    Prevents duplicate check-ins for the same habit on the same day.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id FROM checkins
        WHERE habit_id = ? AND date = ?
    """, (habit_id, today))

    if cursor.fetchone():
        conn.close()
        return "already_checked_in"

    cursor.execute("""
        INSERT INTO checkins (habit_id, date, completed)
        VALUES (?, ?, ?)
    """, (habit_id, today, completed))

    conn.commit()
    conn.close()
    return "recorded"


def already_checked_in_today(habit_id):
    """Return True if this habit was already checked in today."""
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id FROM checkins
        WHERE habit_id = ? AND date = ?
    """, (habit_id, today))
    result = cursor.fetchone() is not None
    conn.close()
    return result


# -----------------------------------------------
# Task 3.1, 3.3 — Daily Check-In UI (Tkinter)
# -----------------------------------------------
def open_checkin(root=None, on_done=None):
    """
    Build and display the Daily Check-In screen.
    Lists every habit with a Done and Missed button for today.
    """
    is_standalone = root is None
    if is_standalone:
        root = tk.Tk()

    root.title("Momentum — Daily Check-In")
    root.geometry("680x500")

    today_str = datetime.now().strftime("%A, %B %d, %Y")
    tk.Label(
        root, text=f"Check-In for {today_str}",
        font=("Helvetica", 16, "bold")
    ).pack(pady=(15, 5))

    tk.Label(
        root, text="Mark each habit as done or missed for today.",
        fg="#666"
    ).pack(pady=(0, 10))

    # --- Scrollable habit list ---
    canvas = tk.Canvas(root)
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    habit_frame = tk.Frame(canvas)

    habit_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=habit_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True, padx=15)
    scrollbar.pack(side="right", fill="y")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, category FROM habits ORDER BY name")
    habits = cursor.fetchall()
    conn.close()

    if not habits:
        tk.Label(
            habit_frame,
            text="No habits created yet. Add one from the Dashboard!",
            fg="#999", font=("Helvetica", 12)
        ).pack(pady=40)
        return

    status_labels = {}

    for idx, (h_id, name, category) in enumerate(habits):
        row = tk.Frame(habit_frame, pady=6)
        row.pack(fill="x", padx=5)

        if idx > 0:
            ttk.Separator(habit_frame, orient="horizontal").pack(fill="x", padx=5)

        initialize_grace_days(h_id)

        streak = calculate_streak(h_id)
        grace = get_grace_days_remaining(h_id)
        checked = already_checked_in_today(h_id)

        info = tk.Frame(row)
        info.pack(side="left", fill="x", expand=True)

        tk.Label(
            info, text=name, font=("Helvetica", 13, "bold"), anchor="w"
        ).pack(anchor="w")

        tk.Label(
            info,
            text=f"{category}  •  🔥 {streak}-day streak  •  {grace} grace day{'s' if grace != 1 else ''} left",
            fg="#555", anchor="w"
        ).pack(anchor="w")

        action = tk.Frame(row)
        action.pack(side="right")

        if checked:
            tk.Label(
                action, text="✔ Done today", fg="green",
                font=("Helvetica", 11, "bold")
            ).pack()
        else:
            status_lbl = tk.Label(action, text="", fg="#333")
            status_labels[h_id] = status_lbl

            def make_done_handler(hid, lbl, btn_d, btn_m):
                def handler():
                    result = record_checkin(hid, completed=1)
                    if result == "already_checked_in":
                        lbl.config(text="Already logged!", fg="orange")
                    else:
                        lbl.config(text="✔ Done!", fg="green")
                        btn_d.config(state="disabled")
                        btn_m.config(state="disabled")
                return handler

            def make_miss_handler(hid, lbl, btn_d, btn_m):
                def handler():
                    used = use_grace_day(hid)
                    record_checkin(hid, completed=0)
                    if used:
                        lbl.config(text="Grace day used", fg="orange")
                    else:
                        lbl.config(text="Streak broken 💔", fg="red")
                    btn_d.config(state="disabled")
                    btn_m.config(state="disabled")
                return handler

            done_btn = tk.Button(action, text="✅ Done", width=8)
            miss_btn = tk.Button(action, text="❌ Missed", width=8)

            done_btn.config(command=make_done_handler(h_id, status_lbl, done_btn, miss_btn))
            miss_btn.config(command=make_miss_handler(h_id, status_lbl, done_btn, miss_btn))

            done_btn.pack(side="left", padx=3)
            miss_btn.pack(side="left", padx=3)
            status_lbl.pack(side="left", padx=8)

    bottom = tk.Frame(root)
    bottom.pack(fill="x", padx=15, pady=10)

    if on_done:
        tk.Button(
            bottom, text="← Back to Dashboard", command=on_done
        ).pack(side="left")

    if is_standalone:
        root.mainloop()


if __name__ == "__main__":
    open_checkin()
