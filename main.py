import tkinter as tk
from tkinter import ttk
from login import LoginApp
import sys
sys.path.append('.')
from admin_dashboard import generate_dummy_students_and_marks
from database import DatabaseManager


def main():
    # Generate dummy data ONCE, then comment/remove this block after first run
    db_manager = DatabaseManager()
    generate_dummy_students_and_marks(db_manager, num_students=50)
    db_manager.close()

    root = tk.Tk()
    root.title("Student Dashboard Portal")
    root.geometry("600x400")
    root.configure(bg="#f0f4f8")

    style = ttk.Style()
    style.theme_use('clam') 
    style.configure('.', font=('Segoe UI', 11))

    # Center the window on the screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"600x400+{x}+{y}")

    app = LoginApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()