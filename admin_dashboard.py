import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
from faker import Faker
import random

class AdminDashboard:
    def __init__(self, master, db_manager, admin_id):
        self.master = master
        self.db_manager = db_manager
        self.admin_id = admin_id

        master.title("Admin Dashboard")
        master.geometry("900x650")
        master.configure(bg="#eef2f3")

        # Header with logout button
        header_frame = tk.Frame(master, bg="#eef2f3")
        header_frame.pack(fill='x', padx=10, pady=(10, 0))
        
        # Title
        tk.Label(header_frame, text="Admin Dashboard", font=("Arial", 16, "bold"), bg="#eef2f3").pack(side='left')
        
        # Logout button
        logout_btn = ttk.Button(header_frame, text="Logout", command=self.logout)
        logout_btn.pack(side='right', padx=10)

        # Custom Styling
        style = ttk.Style()
        style.configure("TButton", font=("Arial", 12), padding=6)
        style.configure("TLabel", font=("Arial", 12))
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"))

        # Notebook (Tabbed UI)
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # Manage Student Marks Tab
        self.marks_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.marks_frame, text='Manage Marks')

        # Attendance Tab
        self.attendance_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.attendance_frame, text='Attendance')
        self.setup_attendance_tab()

        # Curriculum Activities Tab
        self.activities_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.activities_frame, text='Curriculum Activities')
        self.setup_activities_tab()

        # --- Filter Button ---
        filter_btn_frame = ttk.Frame(self.marks_frame)
        filter_btn_frame.pack(fill='x', padx=10, pady=(0,5))
        ttk.Button(filter_btn_frame, text="Filter", command=self.open_filter_popup).pack(side='left')
        # --- End Filter Button ---

        self.tree = ttk.Treeview(self.marks_frame, columns=('Name', 'Subject', 'Marks', 'Participation Bonus', 'Total Marks', 'Result'), show='headings', height=10)
        self.tree.heading('Name', text='Student Name')
        self.tree.heading('Subject', text='Subject')
        self.tree.heading('Marks', text='Marks')
        self.tree.heading('Participation Bonus', text='Participation Bonus')
        self.tree.heading('Total Marks', text='Total Marks')
        self.tree.heading('Result', text='Result')
        self.tree.column("Name", width=150, anchor="center")
        self.tree.column("Subject", width=150, anchor="center")
        self.tree.column("Marks", width=100, anchor="center")
        self.tree.column("Participation Bonus", width=150, anchor="center")
        self.tree.column("Total Marks", width=120, anchor="center")
        self.tree.column("Result", width=100, anchor="center")

        tree_scroll = ttk.Scrollbar(self.marks_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=tree_scroll.set)
        tree_scroll.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Buttons
        btn_frame = ttk.Frame(self.marks_frame)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Add/Edit Marks", command=self.open_marks_window).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(btn_frame, text="Delete Marks", command=self.delete_marks).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(btn_frame, text="View Rankings", command=self.show_rankings).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(btn_frame, text="Subject Chart", command=self.subject_performance_chart).grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(btn_frame, text="Export to CSV", command=self.export_to_csv).grid(row=0, column=4, padx=5, pady=5)

        self.load_students_marks()

    def load_students_marks(self):
        # Store all data for filtering
        self.all_marks_rows = []
        for i in self.tree.get_children():
            self.tree.delete(i)
        marks_data = self.db_manager.get_all_students_marks()
        # marks_data: [(student_id, name, subject, marks)]
        student_averages = {}
        for record in marks_data:
            student_id = record[0]
            if student_id not in student_averages:
                student_averages[student_id] = self.db_manager.calculate_student_average(student_id)

        # --- Load participants from activities.csv ---
        participants = set()
        try:
            with open('activities.csv', newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row:  # skip empty
                        participants.add(row[0].strip())  # Assuming first col is student name
        except FileNotFoundError:
            pass

        subjects_set = set()
        for record in marks_data:
            student_id, name, subject, marks = record
            bonus = 5 if name in participants else 0
            total_marks = marks + bonus
            category = self.get_result_category(student_averages[student_id] + (bonus if len(marks_data) > 0 else 0))
            row = (name, subject, marks, f"+{bonus}" if bonus else "", total_marks, category)
            self.tree.insert('', 'end', values=row)
            self.all_marks_rows.append(row)
            subjects_set.add(subject)

    def get_result_category(self, avg_marks):
        if avg_marks >= 75:
            return "Distinction"
        elif avg_marks < 40:
            return "Fail"
        else:
            return "Pass"

    def open_marks_window(self):
        marks_window = tk.Toplevel(self.master)
        marks_window.title("Add/Edit Marks")
        marks_window.geometry("500x500")

        ttk.Label(marks_window, text="Student Name:").grid(row=0, column=0, padx=10, pady=5)
        student_name_entry = ttk.Entry(marks_window)
        student_name_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(marks_window, text="Subjects and Marks:").grid(row=1, column=0, padx=10, pady=5)

        subjects_frame = ttk.Frame(marks_window)
        subjects_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=5)

        subjects_entries = []

        def add_subject_field():
            row = len(subjects_entries)
            subject_entry = ttk.Entry(subjects_frame, width=15)
            marks_entry = ttk.Entry(subjects_frame, width=10)
            subject_entry.grid(row=row, column=0, padx=5, pady=2)
            marks_entry.grid(row=row, column=1, padx=5, pady=2)
            subjects_entries.append((subject_entry, marks_entry))

        add_subject_field()  # Add one field by default

        ttk.Button(marks_window, text="Add Subject", command=add_subject_field).grid(row=3, column=0, pady=5)

        def save_marks():
            student_name = student_name_entry.get()
            marks_data = []
            for subject_entry, marks_entry in subjects_entries:
                subject = subject_entry.get()
                try:
                    marks = float(marks_entry.get())
                    if marks < 0 or marks > 100:
                        raise ValueError
                except ValueError:
                    messagebox.showerror("Error", "Enter valid marks (0-100).")
                    return
                marks_data.append((student_name, subject, marks))

            for student_name, subject, marks in marks_data:
                self.db_manager.add_student_marks(student_name, subject, marks)

            self.load_students_marks()
            marks_window.destroy()
            messagebox.showinfo("Success", "Marks updated!")

        ttk.Button(marks_window, text="Save", command=save_marks).grid(row=4, columnspan=2, pady=10)

    def delete_marks(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Select", "Select a record to delete.")
            return
        item = self.tree.item(selected_item, "values")
        self.db_manager.delete_student_marks(item[0], item[1])
        self.load_students_marks()
        messagebox.showinfo("Success", "Marks deleted!")

    def show_rankings(self):
        top_students = self.db_manager.get_top_students()
        ranking_window = tk.Toplevel(self.master)
        ranking_window.title("Rankings")
        ranking_window.geometry("400x300")
        tree = ttk.Treeview(ranking_window, columns=('Rank', 'Name', 'Average'), show='headings')
        tree.heading('Rank', text='Rank')
        tree.heading('Name', text='Student Name')
        tree.heading('Average', text='Average Marks')
        tree.column("Rank", width=50, anchor="center")
        tree.column("Name", width=200, anchor="center")
        tree.column("Average", width=100, anchor="center")
        for i, (name, avg_marks) in enumerate(top_students, 1):
            tree.insert('', 'end', values=(i, name, f"{avg_marks:.2f}"))
        tree.pack(padx=10, pady=10, fill='both', expand=True)

    def subject_performance_chart(self):
        marks_data = self.db_manager.get_all_students_marks()
        if not marks_data:
            messagebox.showwarning("No Data", "No marks data available.")
            return

        subject_marks = {}
        for _, _, subject, marks in marks_data:
            if subject not in subject_marks:
                subject_marks[subject] = []
            subject_marks[subject].append(marks)

        subject_avg_marks = {subject: sum(marks) / len(marks) for subject, marks in subject_marks.items()}
        fig, ax = plt.subplots(figsize=(7, 6))
        ax.pie(subject_avg_marks.values(), labels=subject_avg_marks.keys(), autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
        ax.set_title('Subject Performance Distribution')
        chart_window = tk.Toplevel(self.master)
        chart_window.title("Performance Chart")
        canvas = FigureCanvasTkAgg(fig, master=chart_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def export_to_csv(self):
        data = self.db_manager.get_all_students_marks()
        with open("student_marks.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Student Name", "Subject", "Marks"])
            for row in data:
                writer.writerow(row[1:])
        messagebox.showinfo("Export", "Data exported to student_marks.csv")

    def logout(self):
        """Logout and return to login screen"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.master.destroy()
            # Show the login window again
            import login
            root = tk.Tk()
            login.LoginApp(root)

    def setup_attendance_tab(self):
        self.attendance_tree = ttk.Treeview(self.attendance_frame, columns=('Name', 'Date', 'Status'), show='headings', height=10)
        self.attendance_tree.heading('Name', text='Student Name')
        self.attendance_tree.heading('Date', text='Date')
        self.attendance_tree.heading('Status', text='Status')
        self.attendance_tree.column("Name", width=150, anchor="center")
        self.attendance_tree.column("Date", width=100, anchor="center")
        self.attendance_tree.column("Status", width=80, anchor="center")
        self.attendance_tree.pack(fill='both', expand=True, padx=10, pady=10)

        btn_frame = ttk.Frame(self.attendance_frame)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Mark Attendance", command=self.open_attendance_window).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Delete Record", command=self.delete_attendance_record).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Refresh", command=self.load_attendance_records).grid(row=0, column=2, padx=5)
        self.load_attendance_records()

    def setup_activities_tab(self):
        self.activities_tree = ttk.Treeview(self.activities_frame, columns=('Name', 'Activity', 'Date'), show='headings', height=10)
        self.activities_tree.heading('Name', text='Student Name')
        self.activities_tree.heading('Activity', text='Activity')
        self.activities_tree.heading('Date', text='Date')
        self.activities_tree.column("Name", width=150, anchor="center")
        self.activities_tree.column("Activity", width=200, anchor="center")
        self.activities_tree.column("Date", width=100, anchor="center")
        self.activities_tree.pack(fill='both', expand=True, padx=10, pady=10)

        btn_frame = ttk.Frame(self.activities_frame)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Add Activity", command=self.open_activity_window).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Delete Activity", command=self.delete_activity_record).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Refresh", command=self.load_activities_records).grid(row=0, column=2, padx=5)
        self.load_activities_records()

    def open_attendance_window(self):
        win = tk.Toplevel(self.master)
        win.title("Mark Attendance")
        win.geometry("350x200")
        ttk.Label(win, text="Student Name:").grid(row=0, column=0, padx=10, pady=5)
        name_entry = ttk.Entry(win)
        name_entry.grid(row=0, column=1, padx=10, pady=5)
        ttk.Label(win, text="Date (YYYY-MM-DD):").grid(row=1, column=0, padx=10, pady=5)
        date_entry = ttk.Entry(win)
        date_entry.grid(row=1, column=1, padx=10, pady=5)
        ttk.Label(win, text="Status:").grid(row=2, column=0, padx=10, pady=5)
        status_cb = ttk.Combobox(win, values=["Present", "Absent"])
        status_cb.grid(row=2, column=1, padx=10, pady=5)
        def save_attendance():
            name = name_entry.get()
            date = date_entry.get()
            status = status_cb.get()
            if name and date and status:
                # Replace with DB call as needed
                with open('attendance.csv', 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([name, date, status])
                self.load_attendance_records()
                win.destroy()
            else:
                messagebox.showerror("Error", "All fields are required.")
        ttk.Button(win, text="Save", command=save_attendance).grid(row=3, column=0, columnspan=2, pady=10)

    def load_attendance_records(self):
        for i in self.attendance_tree.get_children():
            self.attendance_tree.delete(i)
        try:
            with open('attendance.csv', newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    self.attendance_tree.insert('', 'end', values=row)
        except FileNotFoundError:
            pass

    def delete_attendance_record(self):
        selected = self.attendance_tree.selection()
        if selected:
            all_rows = []
            with open('attendance.csv', newline='') as f:
                reader = csv.reader(f)
                all_rows = list(reader)
            item = self.attendance_tree.item(selected[0])['values']
            all_rows = [row for row in all_rows if row != item]
            with open('attendance.csv', 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(all_rows)
            self.load_attendance_records()

    def open_activity_window(self):
        win = tk.Toplevel(self.master)
        win.title("Add Activity")
        win.geometry("350x200")
        ttk.Label(win, text="Student Name:").grid(row=0, column=0, padx=10, pady=5)
        name_entry = ttk.Entry(win)
        name_entry.grid(row=0, column=1, padx=10, pady=5)
        ttk.Label(win, text="Activity:").grid(row=1, column=0, padx=10, pady=5)
        activity_entry = ttk.Entry(win)
        activity_entry.grid(row=1, column=1, padx=10, pady=5)
        ttk.Label(win, text="Date (YYYY-MM-DD):").grid(row=2, column=0, padx=10, pady=5)
        date_entry = ttk.Entry(win)
        date_entry.grid(row=2, column=1, padx=10, pady=5)
        def save_activity():
            name = name_entry.get()
            activity = activity_entry.get()
            date = date_entry.get()
            if name and activity and date:
                # Replace with DB call as needed
                with open('activities.csv', 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([name, activity, date])
                # --- Add 5 marks participation bonus ---
                # Add 5 marks to the student's first subject (or a default subject like 'Math')
                subjects = ["Math", "Science", "English", "History", "Geography"]
                # Try to get the student's existing subjects from the database
                marks_list = self.db_manager.get_student_marks(name)
                if marks_list:
                    # Add bonus to the first subject found
                    subject = marks_list[0][0]
                    current_marks = marks_list[0][1]
                    self.db_manager.add_student_marks(name, subject, current_marks + 5)
                else:
                    # If student has no marks yet, add 5 marks to 'Math'
                    self.db_manager.add_student_marks(name, "Math", 5)
                self.load_activities_records()
                win.destroy()
            else:
                messagebox.showerror("Error", "All fields are required.")
        ttk.Button(win, text="Save", command=save_activity).grid(row=3, column=0, columnspan=2, pady=10)

    def load_activities_records(self):
        for i in self.activities_tree.get_children():
            self.activities_tree.delete(i)
        try:
            with open('activities.csv', newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    self.activities_tree.insert('', 'end', values=row)
        except FileNotFoundError:
            pass

    def delete_activity_record(self):
        selected = self.activities_tree.selection()
        if selected:
            all_rows = []
            with open('activities.csv', newline='') as f:
                reader = csv.reader(f)
                all_rows = list(reader)
            item = self.activities_tree.item(selected[0])['values']
            all_rows = [row for row in all_rows if row != item]
            with open('activities.csv', 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(all_rows)
            self.load_activities_records()

    def open_filter_popup(self):
        popup = tk.Toplevel(self.master)
        popup.title("Apply Filters")
        popup.geometry("600x180")
        popup.grab_set()

        ttk.Label(popup, text="Student Name:").grid(row=0, column=0, padx=5, pady=5)
        filter_name = ttk.Entry(popup, width=15)
        filter_name.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(popup, text="Subject:").grid(row=0, column=2, padx=5, pady=5)
        filter_subject = ttk.Combobox(popup, values=[""] + sorted({row[1] for row in getattr(self, 'all_marks_rows', [])}), width=12)
        filter_subject.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(popup, text="Result:").grid(row=1, column=0, padx=5, pady=5)
        filter_result = ttk.Combobox(popup, values=["", "Distinction", "Pass", "Fail"], width=12)
        filter_result.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(popup, text="Participation Bonus:").grid(row=1, column=2, padx=5, pady=5)
        filter_bonus = ttk.Combobox(popup, values=["", "Yes", "No"], width=7)
        filter_bonus.grid(row=1, column=3, padx=5, pady=5)

        ttk.Label(popup, text="Min Marks:").grid(row=2, column=0, padx=5, pady=5)
        filter_min_marks = ttk.Entry(popup, width=7)
        filter_min_marks.grid(row=2, column=1, padx=5, pady=5)
        ttk.Label(popup, text="Max Marks:").grid(row=2, column=2, padx=5, pady=5)
        filter_max_marks = ttk.Entry(popup, width=7)
        filter_max_marks.grid(row=2, column=3, padx=5, pady=5)

        def do_apply():
            name = filter_name.get().strip().lower()
            subject = filter_subject.get().strip().lower()
            result = filter_result.get().strip().lower()
            bonus = filter_bonus.get().strip().lower()
            min_marks = filter_min_marks.get().strip()
            max_marks = filter_max_marks.get().strip()
            for i in self.tree.get_children():
                self.tree.delete(i)
            for row in self.all_marks_rows:
                show = True
                if name and name not in row[0].lower():
                    show = False
                if subject and subject != row[1].lower():
                    show = False
                if result and result != row[5].lower():
                    show = False
                if bonus:
                    if bonus == "yes" and row[3] == "":
                        show = False
                    if bonus == "no" and row[3] != "":
                        show = False
                try:
                    if min_marks and float(row[4]) < float(min_marks):
                        show = False
                    if max_marks and float(row[4]) > float(max_marks):
                        show = False
                except:
                    pass
                if show:
                    self.tree.insert('', 'end', values=row)
            popup.destroy()

        ttk.Button(popup, text="Apply", command=do_apply).grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(popup, text="Cancel", command=popup.destroy).grid(row=3, column=2, columnspan=2, pady=10)

def generate_dummy_students_and_marks(db_manager, num_students=50, subjects=None):
    """
    Generate dummy students and marks using Faker and insert into database.
    """
    if subjects is None:
        subjects = ["Math", "Science", "English", "History", "Geography"]
    fake = Faker()
    for _ in range(num_students):
        name = fake.name()
        username = name.lower().replace(" ", "") + str(random.randint(100,999))
        password = "password123"
        email = fake.email()
        # Register user as student
        db_manager.register_user(username, password, "student", name, email)
        # Assign random marks for each subject
        for subject in subjects:
            marks = random.randint(40, 100)
            db_manager.add_student_marks(name, subject, marks)

# Usage example (call this ONCE, e.g., from __main__ or a button):
# generate_dummy_students_and_marks(self.db_manager, num_students=50)
