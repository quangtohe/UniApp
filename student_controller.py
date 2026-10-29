"""Member 1: registration, regex validation, login and the Student System menu."""

import random

from database import Database, DatabaseError
from student import Student
from validator import Validator


class StudentController:
    """Expose reusable account services plus the CLI interactions from the sample I/O."""

    EMAIL_PATTERN = Validator.EMAIL_PATTERN
    PASSWORD_PATTERN = Validator.PASSWORD_PATTERN

    def __init__(self, database=None):
        """Use the application database, or an isolated database supplied by a caller."""
        self.database = database if database is not None else Database()

    @staticmethod
    def validate_email(email):
        """Check an address against the shared university email regex constant."""
        return Validator.validate_email(email)

    @staticmethod
    def validate_password(password):
        """Check the capital-initial, five-letter and three-digit password pattern."""
        return Validator.validate_password(password)

    def generate_student_id(self, students):
        """Generate a six-digit ID and resolve collisions without an unbounded retry."""
        used = {student.student_id for student in students}
        if len(used) >= 999999:
            raise ValueError("No student IDs are available.")
        candidate = random.randint(1, 999999)
        while f"{candidate:06d}" in used:
            candidate = candidate % 999999 + 1
        return f"{candidate:06d}"

    def register(self, name, email, password):
        """Create and persist a valid new student, rejecting empty names and duplicates."""
        name, email = name.strip(), email.strip()
        if not name:
            raise ValueError("Name is required.")
        Validator.require_credentials(email, password)
        students = self.database.read_students()
        if any(student.email.lower() == email.lower() for student in students):
            raise ValueError("Student already exists.")
        student = Student(self.generate_student_id(students), name, email, password)
        self.database.write_students(students + [student])
        return student

    def authenticate(self, email, password):
        """Read the account from disk and return it only when both credentials match."""
        email = email.strip()
        Validator.require_credentials(email, password)
        student = self.database.find_student_by_email(email)
        if student is None or student.password != password:
            raise ValueError("Invalid email or password.")
        return student

    @staticmethod
    def _read_credentials():
        """Repeat CLI credential input until both formats meet the assessment rules."""
        while True:
            email = input("        Email: ").strip()
            password = input("        Password: ")
            if Validator.validate_login_fields(email, password):
                print("        email and password formats acceptable")
                return email, password
            print("        Incorrect email or password format")

    def register_student(self):
        """Follow sign-up order: validate credentials, reject duplicates, then ask name."""
        print("        Student Sign Up")
        email, password = self._read_credentials()
        try:
            existing = self.database.find_student_by_email(email)
            if existing is not None:
                print(f"        Student {existing.name} already exists")
                return None
            name = input("        Name: ").strip()
            while not name:
                print("        Name is required.")
                name = input("        Name: ").strip()
            student = self.register(name, email, password)
        except (ValueError, DatabaseError) as error:
            print(f"        {error}")
            return None
        print(f"        Enrolling Student {student.name}")
        return student

    def login_student(self):
        """Follow sign-in input/retry behavior and return a freshly loaded student."""
        print("        Student Sign In")
        email, password = self._read_credentials()
        try:
            return self.authenticate(email, password)
        except ValueError:
            print("        Student does not exist")
        except DatabaseError as error:
            print(f"        {error}")
        return None

    def student_menu(self):
        """Repeat l/r/x choices and enter the course menu after a successful login."""
        from subject_controller import SubjectController

        while True:
            choice = input("    Student System (l/r/x): ").strip().lower()
            if choice == "l":
                student = self.login_student()
                if student is not None:
                    SubjectController(self.database).subject_menu(student)
            elif choice == "r":
                self.register_student()
            elif choice == "x":
                return
            else:
                print("        Invalid option. Please try again.")


## PRE-CANVAS IMPLEMENTATION - retained as ## comments before course-aligned changes.
## """Member 1: account operations and the Student System CLI."""
## 
## import random
## 
## from database import Database, DatabaseError
## from student import Student
## from validator import Validator
## 
## 
## class StudentController:
##     """Share registration and authentication logic between CLI and GUI."""
## 
##     EMAIL_PATTERN = Validator.EMAIL_PATTERN
##     PASSWORD_PATTERN = Validator.PASSWORD_PATTERN
## 
##     def __init__(self, database=None):
##         """Use the application database or an injected test database."""
##         self.database = database if database is not None else Database()
## 
##     @staticmethod
##     def validate_email(email):
##         """Delegate email validation to the common validator."""
##         return Validator.validate_email(email)
## 
##     @staticmethod
##     def validate_password(password):
##         """Delegate password validation to the common validator."""
##         return Validator.validate_password(password)
## 
##     def generate_student_id(self, students):
##         """Choose an unused ID from 000001 to 999999 with a bounded collision search."""
##         used = {student.student_id for student in students}
##         if len(used) >= 999999:
##             raise ValueError("No student IDs are available.")
##         candidate = random.randint(1, 999999)
##         while f"{candidate:06d}" in used:
##             candidate = candidate % 999999 + 1
##         return f"{candidate:06d}"
## 
##     def register(self, name, email, password):
##         """Validate and persist a new account, rejecting blank names and duplicate emails."""
##         name, email = name.strip(), email.strip()
##         if not name:
##             raise ValueError("Name is required.")
##         Validator.require_credentials(email, password)
##         students = self.database.read_students()
##         if any(student.email.lower() == email.lower() for student in students):
##             raise ValueError("Student already exists.")
##         student = Student(self.generate_student_id(students), name, email, password)
##         self.database.write_students(students + [student])
##         return student
## 
##     def authenticate(self, email, password):
##         """Return the matching account or raise a readable login error."""
##         email = email.strip()
##         Validator.require_credentials(email, password)
##         student = self.database.find_student_by_email(email)
##         if student is None or student.password != password:
##             raise ValueError("Invalid email or password.")
##         return student
## 
##     def register_student(self):
##         """Collect CLI registration fields and display the created student ID."""
##         name = input("Enter your name: ")
##         email = input("Enter your email: ")
##         password = input("Enter your password: ")
##         try:
##             student = self.register(name, email, password)
##         except (ValueError, DatabaseError) as error:
##             print(error)
##             return None
##         print(f"Registration successful. Student ID: {student.student_id}")
##         return student
## 
##     def login_student(self):
##         """Collect CLI login fields and return the authenticated student."""
##         email = input("Enter your email: ")
##         password = input("Enter your password: ")
##         try:
##             student = self.authenticate(email, password)
##         except (ValueError, DatabaseError) as error:
##             print(error)
##             return None
##         print(f"Login successful. Welcome, {student.name}.")
##         return student
## 
##     def student_menu(self):
##         """Run login/register actions and return to University Menu on exit."""
##         from subject_controller import SubjectController
## 
##         while True:
##             print("\nStudent System: (l) login, (r) register, (x) return")
##             choice = input("Choose an option: ").strip().lower()
##             if choice == "l":
##                 student = self.login_student()
##                 if student is not None:
##                     SubjectController(self.database).subject_menu(student)
##             elif choice == "r":
##                 self.register_student()
##             elif choice == "x":
##                 return
##             else:
##                 print("Invalid option. Please try again.")

## ORIGINAL CODE - retained as requested; active implementation appears above.
## import re
## import random
## 
## from student import Student
## from database import Database
## 
## class StudentController:
## 
##     EMAIL_PATTERN = r"^[A-Za-z0-9._%+-]+@university\.com$"
##     PASSWORD_PATTERN = r"^[A-Z][A-Za-z]{4,}\d{3,}$"
## 
##     def __init__(self):
##         self.database = Database()
## 
##     def validate_email(self, email):
##         return re.fullmatch(self.EMAIL_PATTERN, email) is not None
## 
##     def validate_password(self, password):
##         return re.fullmatch(self.PASSWORD_PATTERN, password) is not None
## 
##     def generate_student_id(self, students):
##         while True:
##             student_id = f"{random.randint(1, 999999):06d}"
##             if all(student.student_id != student_id for student in students):
##                 return student_id
## 
##     def register_student(self):
##         name = input("Enter your name: ")
##         email = input("Enter your email: ")
##         password = input("Enter your password: ")
##         if not self.validate_email(email):
##             print("Invalid email format.")
##             return
##         if not self.validate_password(password):
##             print("Invalid password format.")
##             return
##         students = self.database.read_students()
##         for student in students:
##             if student.email == email:
##                 print("Student already exists.")
##                 return
##         student_id = self.generate_student_id(students)
##         new_student = Student(student_id, name, email, password)
##         students.append(new_student)
##         self.database.write_students(students)
##         print("Registration successful")
##         print("Student ID:", student_id)
## 
##     def login_student(self):
##         email = input("Enter your email: ")
##         password = input("Enter your password: ")
##         if not self.validate_email(email):
##             print("Invalid email format.")
##             return None
##         if not self.validate_password(password):
##             print("Invalid password format.")
##             return None
##         students = self.database.read_students()
##         for student in students:
##             if student.email == email and student.password == password:
##                 print("Login successful")
##                 return student
##         print("Invalid email or password.")
##         return None
## 
##     def student_menu(self):
##         while True:
##             print("\nStudent System")
##             print("(l) login")
##             print("(r) register")
##             print("(x) exit")
##             choice = input("Choose an option: ").lower()
##             
##             if choice == 'l':
##                 student = self.login_student()
##                 if student is not None:
##                     print("Welcome,", student.name)
##                     from subject_controller import SubjectController
##                     subject_controller = SubjectController()
##                     subject_controller.subject_menu(student)
##             elif choice == 'r':
##                 self.register_student()
##             elif choice == 'x':
##                 print("Exiting Student System.")
##                 break
##             else:
##                 print("Invalid option. Please try again.")
