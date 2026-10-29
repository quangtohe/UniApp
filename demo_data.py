"""Create an explicit, portable demo account without changing students.data."""

from pathlib import Path

from database import Database
from student_controller import StudentController


DEMO_EMAIL = "preview@university.com"
DEMO_PASSWORD = "Abcde123"
DEMO_NAME = "Demo Student"


def create_demo_database(filename=None):
    """Ensure known demo credentials in demo.data while preserving existing enrolments."""
    path = Path(filename) if filename is not None else Path(__file__).with_name("demo.data")
    database = Database(path)
    students = database.read_students()
    demo = next((student for student in students if student.email.lower() == DEMO_EMAIL), None)
    if demo is None:
        StudentController(database).register(DEMO_NAME, DEMO_EMAIL, DEMO_PASSWORD)
    elif demo.password != DEMO_PASSWORD:
        # Explicit demo mode restores only the public demo password, not other records.
        demo.change_password(DEMO_PASSWORD)
        database.write_students(students)
    return database
