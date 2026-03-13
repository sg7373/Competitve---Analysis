import tkinter as tk
from tkinter import ttk, messagebox
import database
import admin_dashboard
import student_dashboard

class LoginApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Student Performance Management System")
        self.master.geometry("400x350")
        self.master.resizable(False, False)

        # Database initialization
        self.db_manager = database.DatabaseManager()

        # Styling
        style = ttk.Style()
        style.configure("TButton", font=("Arial", 12), padding=5)
        style.configure("TLabel", font=("Arial", 11))
        style.configure("TEntry", padding=5)

        # Main Frame
        self.login_frame = ttk.LabelFrame(master, text="Login", padding=20)
        self.login_frame.pack(pady=30, padx=30, fill="both")

        # Username
        ttk.Label(self.login_frame, text="Username:").grid(row=0, column=0, sticky="w", pady=5)
        self.username_entry = ttk.Entry(self.login_frame, width=30)
        self.username_entry.grid(row=0, column=1, pady=5)

        # Password
        ttk.Label(self.login_frame, text="Password:").grid(row=1, column=0, sticky="w", pady=5)
        self.password_entry = ttk.Entry(self.login_frame, show="*", width=30)
        self.password_entry.grid(row=1, column=1, pady=5)

        # Login Button
        ttk.Button(self.login_frame, text="Login", command=self.login).grid(row=2, columnspan=2, pady=10)

        # Signup Button
        ttk.Button(self.master, text="Signup", command=self.signup).pack(pady=5)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Input Error", "Please enter both username and password")
            return

        user_data = self.db_manager.validate_login(username, password)

        if user_data:
            user_id, role = user_data
            self.master.withdraw()  # Hide login window

            if role == 'admin':
                admin_window = tk.Toplevel(self.master)
                admin_dashboard.AdminDashboard(admin_window, self.db_manager, user_id)
            else:
                student_window = tk.Toplevel(self.master)
                student_dashboard.StudentDashboard(student_window, self.db_manager, user_id)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def signup(self):
        signup_window = tk.Toplevel(self.master)
        signup_window.title("Signup")
        signup_window.geometry("350x450")
        signup_window.resizable(False, False)

        ttk.Label(signup_window, text="Signup Form", font=("Arial", 14, "bold")).pack(pady=10)

        form_frame = ttk.Frame(signup_window, padding=10)
        form_frame.pack(pady=10, padx=20, fill="both")

        ttk.Label(form_frame, text="Name:").grid(row=0, column=0, sticky="w", pady=5)
        name_entry = ttk.Entry(form_frame, width=30)
        name_entry.grid(row=0, column=1, pady=5)

        ttk.Label(form_frame, text="Email:").grid(row=1, column=0, sticky="w", pady=5)
        email_entry = ttk.Entry(form_frame, width=30)
        email_entry.grid(row=1, column=1, pady=5)

        ttk.Label(form_frame, text="Username:").grid(row=2, column=0, sticky="w", pady=5)
        username_entry = ttk.Entry(form_frame, width=30)
        username_entry.grid(row=2, column=1, pady=5)

        ttk.Label(form_frame, text="Password:").grid(row=3, column=0, sticky="w", pady=5)
        password_entry = ttk.Entry(form_frame, show="*", width=30)
        password_entry.grid(row=3, column=1, pady=5)

        ttk.Label(form_frame, text="Role:").grid(row=4, column=0, sticky="w", pady=5)
        role_var = tk.StringVar(value="student")
        ttk.Radiobutton(form_frame, text="Student", variable=role_var, value="student").grid(row=4, column=1, sticky="w")
        ttk.Radiobutton(form_frame, text="Admin", variable=role_var, value="admin").grid(row=5, column=1, sticky="w")

        def register():
            if not all([name_entry.get(), email_entry.get(), username_entry.get(), password_entry.get()]):
                messagebox.showwarning("Input Error", "All fields are required!")
                return

            result = self.db_manager.register_user(
                username_entry.get(), 
                password_entry.get(), 
                role_var.get(),
                name_entry.get(),
                email_entry.get()
            )
            if result:
                messagebox.showinfo("Success", "User registered successfully!")
                signup_window.destroy()
            else:
                messagebox.showerror("Error", "Username already exists")

        ttk.Button(signup_window, text="Register", command=register).pack(pady=15)