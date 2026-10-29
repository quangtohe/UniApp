"""Launch CLI/GUI with production data or an explicitly selected demo database."""

import argparse

from database import Database, DatabaseError
from demo_data import DEMO_EMAIL, DEMO_PASSWORD, create_demo_database


def main(argv=None):
    """Choose an interface and initialise the requested database before launching."""
    parser = argparse.ArgumentParser(description="Group 7 University Application")
    parser.add_argument("--gui", action="store_true", help="Open the registered-student Tkinter interface")
    data_options = parser.add_mutually_exclusive_group()
    data_options.add_argument("--data", help="Use a separate students.data path for demos or testing")
    data_options.add_argument("--demo", action="store_true", help="Create/use demo.data with a ready-to-use demo account")
    args = parser.parse_args(argv)
    try:
        database = create_demo_database() if args.demo else Database(args.data)
        if args.gui:
            from gui_uni_app import GUIUniApp

            application = GUIUniApp(database=database)
            if args.demo:
                application.email_var.set(DEMO_EMAIL)
                application.password_var.set(DEMO_PASSWORD)
                application.root.title("University Application | Demo Login")
            application.run()
        else:
            from cli_uni_app import CLIUniApp

            if args.demo:
                print(f"Demo account: {DEMO_EMAIL} | Password: {DEMO_PASSWORD}")
            CLIUniApp(database).run()
    except DatabaseError as error:
        print(error)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


## PRE-DEMO ENTRY POINT - retained as ## comments; active implementation appears above.
## """Launch the integrated CLI by default or the registered-student GUI with --gui."""
## 
## import argparse
## 
## from database import Database, DatabaseError
## 
## 
## def main(argv=None):
##     """Parse interface/data options and launch without running anything on import."""
##     parser = argparse.ArgumentParser(description="Group 7 University Application")
##     parser.add_argument("--gui", action="store_true", help="Open the registered-student Tkinter interface")
##     parser.add_argument("--data", help="Use a separate students.data path for demos or testing")
##     args = parser.parse_args(argv)
##     try:
##         database = Database(args.data)
##         if args.gui:
##             from gui_uni_app import GUIUniApp
## 
##             GUIUniApp(database=database).run()
##         else:
##             from cli_uni_app import CLIUniApp
## 
##             CLIUniApp(database).run()
##     except DatabaseError as error:
##         print(error)
##         return 1
##     return 0
## 
## 
## if __name__ == "__main__":
##     raise SystemExit(main())

## ORIGINAL CODE - retained as requested; active implementation appears above.
## from student_controller import StudentController
## student_controller = StudentController()
## student_controller.student_menu()
## 
## 
## 
## 
## 
## 
## 
## 
## 
## 
## 
## 
## 
## 
## 
## 
## 
## 
## # students = database.read_students()
## 
## 
## # EMAIL_PATTERN = r"^[A-Za-z0-9._%+-]+@university\.com$"
## # PASSWORD_PATTERN = r"^[A-Z][A-Za-z]{4,}\d{3,}$"
## 
## # def validate_email(email):
## #     return re.fullmatch(EMAIL_PATTERN, email) is not None
## # def validate_password(password):
## #     return re.fullmatch(PASSWORD_PATTERN, password) is not None
## 
## # def student_menu():
## #     while True:
## #         print("\nStudent System")
## #         print("(l) login")
## #         print("(r) register")
## #         print("(x) exit")
## #         choice = input("Choose an option: ").lower()
## #         if choice == 'l':
## #             student = login_student()
## #             if student is not None:
## #                 print("Welcome,", student.name)
## #         elif choice == 'r':
## #             register_student()
## #         elif choice == 'x':
## #             print("Exiting Student System.")
## #             break
## #         else:
## #             print("Invalid option. Please try again.")
## 
## # def register_student():
## #     name = input("Enter your name: ")
## #     email = input("Enter your email: ")
## #     password = input("Enter your password: ")
## #     if not validate_email(email):
## #         print("Invalid email format.")
##         
## #     if not validate_password(password):
## #         print("Invalid password format.")
## #         return
## #     students = database.read_students()
## #     for student in students:
## #         if student.email == email:
## #             print("Student already exists.")
## #             return
## #     student_id = generate_student_id(students)
## #     new_student = Student(student_id, name, email, password)
## #     students.append(new_student)
## #     database.write_students(students)
## #     print("Registration successful")
## #     print("Student ID:", student_id)
## 
## # def generate_student_id(students):
## #     while True:
## #         student_id = f"{random.randint(1, 999999):06d}"
## #         if all(student.student_id != student_id for student in students):
## #             return student_id
## 
## # def login_student():
## #     email = input("Enter your email: ")
## #     password = input("Enter your password: ")
## #     if not validate_email(email):
## #         print("Invalid email format.")
## #         return None
## #     if not validate_password(password):
## #         print("Invalid password format.")
## #         return None
## #     students = database.read_students()
## #     for student in students:
## #         if student.email == email and student.password == password:
## #             print("Login successful")
## #             return student
## #     print("Invalid email or password.")
## #     return None
## 
## # student_menu()
