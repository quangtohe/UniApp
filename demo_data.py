"""Member 4: isolated demonstration data for testing the integrated CLI and GUI."""

from pathlib import Path

from database import Database
from student import Student
from student_controller import StudentController


DEMO_EMAIL = "preview@university.com"
DEMO_PASSWORD = "Abcde123"
DEMO_ADMIN_EMAIL = "admin@university.com"
DEMO_ADMIN_PASSWORD = "Admin123"


def create_demo_database(filename=None):
    """Create a separate demo account and retain its enrolments on later demo runs."""
    path = Path(filename) if filename is not None else Path(__file__).with_name("demo.data")
    Database.configure_default(path)
    database = Database(path)
    students = database.read_students()
    demo = next((student for student in students if student.email == DEMO_EMAIL), None)
    if demo is None:
        account_controller = StudentController()
        account_controller.database = database
        student_id = account_controller.generate_student_id(students)
        students.append(Student(student_id, "Demo Student", DEMO_EMAIL, DEMO_PASSWORD))
        database.write_students(students)
    elif demo.password != DEMO_PASSWORD:
        demo.change_password(DEMO_PASSWORD)
        database.write_students(students)
    return database
