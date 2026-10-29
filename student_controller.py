import re
import random

from student import Student
from database import Database

class StudentController:

    EMAIL_PATTERN = r"^[A-Za-z0-9._%+-]+@university\.com$"
    PASSWORD_PATTERN = r"^[A-Z][A-Za-z]{4,}\d{3,}$"

    def __init__(self):
        self.database = Database()

    def validate_email(self, email):
        return re.fullmatch(self.EMAIL_PATTERN, email) is not None

    def validate_password(self, password):
        return re.fullmatch(self.PASSWORD_PATTERN, password) is not None

    def generate_student_id(self, students):
        while True:
            student_id = f"{random.randint(1, 999999):06d}"
            if all(student.student_id != student_id for student in students):
                return student_id

    def register_student(self):
        name = input("Enter your name: ")
        email = input("Enter your email: ")
        password = input("Enter your password: ")
        if not self.validate_email(email):
            print("Invalid email format.")
            return
        if not self.validate_password(password):
            print("Invalid password format.")
            return
        students = self.database.read_students()
        for student in students:
            if student.email == email:
                print("Student already exists.")
                return
        student_id = self.generate_student_id(students)
        new_student = Student(student_id, name, email, password)
        students.append(new_student)
        self.database.write_students(students)
        print("Registration successful")
        print("Student ID:", student_id)

    def login_student(self):
        email = input("Enter your email: ")
        password = input("Enter your password: ")
        if not self.validate_email(email):
            print("Invalid email format.")
            return None
        if not self.validate_password(password):
            print("Invalid password format.")
            return None
        students = self.database.read_students()
        for student in students:
            if student.email == email and student.password == password:
                print("Login successful")
                return student
        print("Invalid email or password.")
        return None

    def student_menu(self):
        while True:
            print("\nStudent System")
            print("(l) login")
            print("(r) register")
            print("(x) exit")
            choice = input("Choose an option: ").lower()
            
            if choice == 'l':
                student = self.login_student()
                if student is not None:
                    print("Welcome,", student.name)
                    from subject_controller import SubjectController
                    subject_controller = SubjectController()
                    subject_controller.subject_menu(student)
            elif choice == 'r':
                self.register_student()
            elif choice == 'x':
                print("Exiting Student System.")
                break
            else:
                print("Invalid option. Please try again.")