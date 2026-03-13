import sqlite3
import hashlib
import datetime

class DatabaseManager:
    def __init__(self, db_name='student_performance.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """Create necessary tables for the application"""
        # Users table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            name TEXT,
            email TEXT
        )''')

        # Marks table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS marks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            subject TEXT NOT NULL,
            marks REAL NOT NULL,
            date TEXT,
            FOREIGN KEY(student_id) REFERENCES users(id)
        )''')
        
        # Check if date column exists, add it if it doesn't
        try:
            self.cursor.execute("SELECT date FROM marks LIMIT 1")
        except sqlite3.OperationalError:
            # Date column doesn't exist, add it (without default value)
            self.cursor.execute("ALTER TABLE marks ADD COLUMN date TEXT")
            
            # Update existing records with current date
            current_date = datetime.datetime.now().strftime("%Y-%m-%d")
            self.cursor.execute("UPDATE marks SET date = ? WHERE date IS NULL", (current_date,))
            
        self.conn.commit()

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username, password, role, name, email):
        hashed_password = self.hash_password(password)
        try:
            self.cursor.execute('''
            INSERT INTO users (username, password, role, name, email) 
            VALUES (?, ?, ?, ?, ?)
            ''', (username, hashed_password, role, name, email))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def validate_login(self, username, password):
        """Validate user login credentials"""
        hashed_password = self.hash_password(password)
        self.cursor.execute('''
        SELECT id, role FROM users 
        WHERE username = ? AND password = ?
        ''', (username, hashed_password))
        return self.cursor.fetchone()

    def add_student_marks(self, student_name, subject, marks):
        """Add or update student marks"""
        # First get the student_id from the name
        self.cursor.execute('''
        SELECT id FROM users 
        WHERE name = ? AND role = 'student'
        ''', (student_name,))
        student = self.cursor.fetchone()
        
        if not student:
            # If student doesn't exist, create a new user with default credentials
            username = student_name.lower().replace(" ", "")
            default_password = self.hash_password("password123")
            self.cursor.execute('''
            INSERT INTO users (username, password, role, name, email) 
            VALUES (?, ?, ?, ?, ?)
            ''', (username, default_password, 'student', student_name, ''))
            student_id = self.cursor.lastrowid
        else:
            student_id = student[0]
            
        # Check if marks already exist for this student and subject
        self.cursor.execute('''
        SELECT id FROM marks 
        WHERE student_id = ? AND subject = ?
        ''', (student_id, subject))
        existing = self.cursor.fetchone()
        
        # Get current date
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        if existing:
            # Update existing marks
            self.cursor.execute('''
            UPDATE marks SET marks = ?, date = ? 
            WHERE student_id = ? AND subject = ?
            ''', (marks, current_date, student_id, subject))
        else:
            # Insert new marks
            self.cursor.execute('''
            INSERT INTO marks (student_id, subject, marks, date) 
            VALUES (?, ?, ?, ?)
            ''', (student_id, subject, marks, current_date))
        
        self.conn.commit()

    def delete_student_marks(self, student_name, subject):
        """Delete marks for a specific student and subject"""
        # First get the student_id from the name
        self.cursor.execute('''
        SELECT id FROM users 
        WHERE name = ? AND role = 'student'
        ''', (student_name,))
        student = self.cursor.fetchone()
        
        if not student:
            return False
            
        student_id = student[0]
        
        self.cursor.execute('''
        DELETE FROM marks 
        WHERE student_id = ? AND subject = ?
        ''', (student_id, subject))
        self.conn.commit()
        return True

    def get_student_marks(self, student_id_or_name):
        """Retrieve marks for a specific student"""
        # Check if input is an ID (integer) or name (string)
        if isinstance(student_id_or_name, int):
            student_id = student_id_or_name
        else:
            # Get student_id from name
            self.cursor.execute('''
            SELECT id FROM users 
            WHERE name = ? AND role = 'student'
            ''', (student_id_or_name,))
            student = self.cursor.fetchone()
            
            if not student:
                return []
                
            student_id = student[0]
        
        self.cursor.execute('''
        SELECT subject, marks FROM marks 
        WHERE student_id = ?
        ''', (student_id,))
        return self.cursor.fetchall()

    def get_all_students_marks(self):
        """Get marks for all students"""
        self.cursor.execute('''
        SELECT u.id, u.name, m.subject, m.marks 
        FROM users u
        JOIN marks m ON u.id = m.student_id
        WHERE u.role = 'student'
        ''')
        return self.cursor.fetchall()

    def calculate_student_average(self, student_id_or_name):
        """Calculate average marks for a student"""
        # Check if input is an ID (integer) or name (string)
        if isinstance(student_id_or_name, int):
            student_id = student_id_or_name
        else:
            # Get student_id from name
            self.cursor.execute('''
            SELECT id FROM users 
            WHERE name = ? AND role = 'student'
            ''', (student_id_or_name,))
            student = self.cursor.fetchone()
            
            if not student:
                return 0
                
            student_id = student[0]
        
        self.cursor.execute('''
        SELECT AVG(marks) FROM marks 
        WHERE student_id = ?
        ''', (student_id,))
        result = self.cursor.fetchone()[0]
        return result if result else 0

    def get_class_average(self, subject):
        """Get the average marks of all students in a specific subject"""
        self.cursor.execute('''
        SELECT AVG(marks) FROM marks 
        WHERE subject = ?
        ''', (subject,))
        avg = self.cursor.fetchone()[0]
        return avg if avg else 0

    def get_student_marks_history(self, student_id_or_name):
        """Retrieve historical marks of a student over multiple tests"""
        # Check if input is an ID (integer) or name (string)
        if isinstance(student_id_or_name, int):
            student_id = student_id_or_name
        else:
            # Get student_id from name
            self.cursor.execute('''
            SELECT id FROM users 
            WHERE name = ? AND role = 'student'
            ''', (student_id_or_name,))
            student = self.cursor.fetchone()
            
            if not student:
                return []
                
            student_id = student[0]
        
        self.cursor.execute('''
        SELECT subject, marks, date FROM marks 
        WHERE student_id = ? ORDER BY date
        ''', (student_id,))
        return self.cursor.fetchall()

    def get_top_students(self, limit=5):
        """Get top students based on average marks"""
        self.cursor.execute('''
        SELECT u.name, AVG(m.marks) as avg_marks 
        FROM users u
        JOIN marks m ON u.id = m.student_id
        WHERE u.role = 'student'
        GROUP BY u.id 
        ORDER BY avg_marks DESC 
        LIMIT ?
        ''', (limit,))
        return self.cursor.fetchall()

    def get_student_name(self, student_id):
        """Retrieve student name by their ID"""
        self.cursor.execute('''
        SELECT name FROM users 
        WHERE id = ? AND role = 'student'
        ''', (student_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def close(self):
        """Close database connection"""
        self.conn.close()
