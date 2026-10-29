from student_controller import StudentController
student_controller = StudentController()
student_controller.student_menu()


















# students = database.read_students()


# EMAIL_PATTERN = r"^[A-Za-z0-9._%+-]+@university\.com$"
# PASSWORD_PATTERN = r"^[A-Z][A-Za-z]{4,}\d{3,}$"

# def validate_email(email):
#     return re.fullmatch(EMAIL_PATTERN, email) is not None
# def validate_password(password):
#     return re.fullmatch(PASSWORD_PATTERN, password) is not None

# def student_menu():
#     while True:
#         print("\nStudent System")
#         print("(l) login")
#         print("(r) register")
#         print("(x) exit")
#         choice = input("Choose an option: ").lower()
#         if choice == 'l':
#             student = login_student()
#             if student is not None:
#                 print("Welcome,", student.name)
#         elif choice == 'r':
#             register_student()
#         elif choice == 'x':
#             print("Exiting Student System.")
#             break
#         else:
#             print("Invalid option. Please try again.")

# def register_student():
#     name = input("Enter your name: ")
#     email = input("Enter your email: ")
#     password = input("Enter your password: ")
#     if not validate_email(email):
#         print("Invalid email format.")
        
#     if not validate_password(password):
#         print("Invalid password format.")
#         return
#     students = database.read_students()
#     for student in students:
#         if student.email == email:
#             print("Student already exists.")
#             return
#     student_id = generate_student_id(students)
#     new_student = Student(student_id, name, email, password)
#     students.append(new_student)
#     database.write_students(students)
#     print("Registration successful")
#     print("Student ID:", student_id)

# def generate_student_id(students):
#     while True:
#         student_id = f"{random.randint(1, 999999):06d}"
#         if all(student.student_id != student_id for student in students):
#             return student_id

# def login_student():
#     email = input("Enter your email: ")
#     password = input("Enter your password: ")
#     if not validate_email(email):
#         print("Invalid email format.")
#         return None
#     if not validate_password(password):
#         print("Invalid password format.")
#         return None
#     students = database.read_students()
#     for student in students:
#         if student.email == email and student.password == password:
#             print("Login successful")
#             return student
#     print("Invalid email or password.")
#     return None

# student_menu()