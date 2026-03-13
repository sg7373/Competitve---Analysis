import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np  # For predictive analysis

class StudentDashboard:
    def __init__(self, master, db_manager, student_id):
        self.master = master
        self.db_manager = db_manager
        self.student_id = student_id
        
        master.title("Student Dashboard")
        master.geometry("900x650")
        master.configure(bg='#f0f0f0')
        
        # Header with logout button
        header_frame = tk.Frame(master, bg='#f0f0f0')
        header_frame.pack(fill='x', padx=10, pady=(10, 0))
        
        # Title
        tk.Label(header_frame, text="Student Dashboard", font=("Arial", 16, "bold"), bg='#f0f0f0').pack(side='left')
        
        # Logout button
        logout_btn = ttk.Button(header_frame, text="Logout", command=self.logout)
        logout_btn.pack(side='right', padx=10)
        
        # Create Notebook (Tabs)
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Personal Marks Tab
        self.marks_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.marks_frame, text='📊 My Marks')
        
        # Attendance Tab
        self.attendance_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.attendance_frame, text='📅 Attendance')
        self.setup_attendance_tab()

        # Curriculum Activities Tab
        self.activities_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.activities_frame, text='🎯 Activities')
        self.setup_activities_tab()
        
        # Marks Table
        self.tree = ttk.Treeview(self.marks_frame, columns=('Subject', 'Marks', 'Class Avg'), show='headings', height=8)
        self.tree.heading('Subject', text='Subject')
        self.tree.heading('Marks', text='Marks')
        self.tree.heading('Class Avg', text='Class Average')
        self.tree.column('Subject', width=200, anchor='center')
        self.tree.column('Marks', width=100, anchor='center')
        self.tree.column('Class Avg', width=100, anchor='center')
        
        scrollbar = ttk.Scrollbar(self.marks_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        # Performance Summary
        self.summary_label = tk.Label(self.marks_frame, text="", font=("Arial", 12, "bold"), fg='#333', bg='#f0f0f0')
        self.summary_label.grid(row=1, column=0, pady=10)
        
        # Buttons
        button_frame = tk.Frame(self.marks_frame, bg='#f0f0f0')
        button_frame.grid(row=2, column=0, pady=10)
        
        ttk.Button(button_frame, text="📈 View Performance Chart", command=self.performance_chart).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(button_frame, text="📊 Trend Analysis", command=self.trend_analysis).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(button_frame, text="🏆 View Top Performers", command=self.view_top_performers).grid(row=0, column=2, padx=5, pady=5)
        
        # Load initial data
        self.load_student_marks()
    
    def load_student_marks(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        marks_data = self.db_manager.get_student_marks(self.student_id)
        for subject, marks in marks_data:
            class_avg = self.db_manager.get_class_average(subject)
            self.tree.insert('', 'end', values=(subject, marks, f"{class_avg:.2f}"))
        
        avg_marks = self.db_manager.calculate_student_average(self.student_id)
        improvement_message = self.get_improvement_message(avg_marks)
        category = self.get_result_category(avg_marks)
        self.summary_label.config(text=f"Your Average Marks: {avg_marks:.2f}\n{improvement_message}\nResult: {category}")
    
    def performance_chart(self):
        marks_data = self.db_manager.get_student_marks(self.student_id)
        subjects = [record[0] for record in marks_data]
        marks = [record[1] for record in marks_data]
        
        fig, ax = plt.subplots(figsize=(8, 6))
        bars = ax.bar(subjects, marks, color=['#4CAF50', '#FF9800', '#2196F3', '#9C27B0', '#FF5722'])
        ax.set_title('My Subject Performance', fontsize=14)
        ax.set_xlabel('Subjects', fontsize=12)
        ax.set_ylabel('Marks', fontsize=12)
        ax.set_xticklabels(subjects, rotation=45, ha='right')
        
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval + 1, round(yval, 2), ha='center', va='bottom', fontsize=10)
        
        chart_window = tk.Toplevel(self.master)
        chart_window.title("Performance Chart")
        
        canvas = FigureCanvasTkAgg(fig, master=chart_window)
        canvas.draw()
        canvas.get_tk_widget().pack()
    
    def trend_analysis(self):
        marks_data = self.db_manager.get_student_marks_history(self.student_id)
        if not marks_data:
            tk.messagebox.showinfo("No Data", "No historical data available for trend analysis.")
            return
            
        # Sort data by date if available
        marks_data.sort(key=lambda x: x[2] if len(x) > 2 else "")
        
        # Extract subjects and scores
        subjects = [record[0] for record in marks_data]
        scores = [record[1] for record in marks_data]
        
        # Create a figure for the trend analysis
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(range(len(subjects)), scores, marker='o', linestyle='-', color='b', label='Your Score')
        
        # Set x-axis labels to be the subjects
        ax.set_xticks(range(len(subjects)))
        ax.set_xticklabels(subjects, rotation=45, ha='right')
        
        ax.set_title('Performance Over Time', fontsize=14)
        ax.set_xlabel('Subjects', fontsize=12)
        ax.set_ylabel('Marks', fontsize=12)
        ax.legend()
        
        # Add a grid for better readability
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Ensure layout fits well
        plt.tight_layout()
        
        trend_window = tk.Toplevel(self.master)
        trend_window.title("Performance Trend Analysis")
        
        canvas = FigureCanvasTkAgg(fig, master=trend_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def view_top_performers(self):
        top_students = self.db_manager.get_top_students()
        
        top_window = tk.Toplevel(self.master)
        top_window.title("Top Performers")
        top_window.geometry("450x350")
        
        tree = ttk.Treeview(top_window, columns=('Rank', 'Name', 'Average'), show='headings', height=10)
        tree.heading('Rank', text='Rank')
        tree.heading('Name', text='Student Name')
        tree.heading('Average', text='Average Marks')
        
        for i, (name, avg_marks) in enumerate(top_students, 1):
            tree.insert('', 'end', values=(i, name, f"{avg_marks:.2f}"))
        tree.pack()
    
    def get_improvement_message(self, avg_marks):
        if avg_marks >= 90:
            return "🌟 Excellent Performance! Keep up the great work!"
        elif avg_marks >= 80:
            return "👍 Good job! Keep working hard!"
        elif avg_marks >= 70:
            return "⚡ Average Performance. Focus on weak subjects."
        else:
            return "🚨 Need Improvement. Study Smart!"
    
    def get_result_category(self, avg_marks):
        if avg_marks >= 75:
            return "Distinction"
        elif avg_marks < 40:
            return "Fail"
        else:
            return "Pass"
    
    def logout(self):
        """Logout and return to login screen"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.master.destroy()
            # Show the login window again
            import login
            root = tk.Tk()
            login.LoginApp(root)
    
    def setup_attendance_tab(self):
        self.attendance_tree = ttk.Treeview(self.attendance_frame, columns=('Date', 'Status'), show='headings', height=10)
        self.attendance_tree.heading('Date', text='Date')
        self.attendance_tree.heading('Status', text='Status')
        self.attendance_tree.column('Date', width=120)
        self.attendance_tree.column('Status', width=100)
        self.attendance_tree.pack(fill='both', expand=True, padx=10, pady=10)
        self.load_attendance_records()

    def setup_activities_tab(self):
        self.activities_tree = ttk.Treeview(self.activities_frame, columns=('Activity', 'Date'), show='headings', height=10)
        self.activities_tree.heading('Activity', text='Activity')
        self.activities_tree.heading('Date', text='Date')
        self.activities_tree.column('Activity', width=200)
        self.activities_tree.column('Date', width=120)
        self.activities_tree.pack(fill='both', expand=True, padx=10, pady=10)
        self.load_activities_records()

    def load_attendance_records(self):
        for i in self.attendance_tree.get_children():
            self.attendance_tree.delete(i)
        try:
            import csv
            with open('attendance.csv', newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) == 3 and row[0].strip().lower() == self.db_manager.get_student_name(self.student_id).strip().lower():
                        self.attendance_tree.insert('', 'end', values=(row[1], row[2]))
        except FileNotFoundError:
            pass

    def load_activities_records(self):
        for i in self.activities_tree.get_children():
            self.activities_tree.delete(i)
        try:
            import csv
            with open('activities.csv', newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) == 3 and row[0].strip().lower() == self.db_manager.get_student_name(self.student_id).strip().lower():
                        self.activities_tree.insert('', 'end', values=(row[1], row[2]))
        except FileNotFoundError:
            pass