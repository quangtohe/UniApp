"""Member 4: adapt the existing group controllers to noninteractive Tkinter callbacks."""

from contextlib import redirect_stdout
from io import StringIO

from admin_controller import AdminController
from database import Database
from student_controller import StudentController
from subject_controller import SubjectController
from student import Student


class GUIController:
    """Reuse existing validation, enrolment and average calculations in the GUI."""

    def __init__(self, database=None):
        """Bind legacy controller instances to the application's selected database."""
        self.database = database if database is not None else Database()
        Database.configure_default(self.database.filename)
        self.account_controller = StudentController()
        self.subject_controller = SubjectController()
        self.account_controller.database = self.database
        self.subject_controller.database = self.database

    def authenticate(self, email, password):
        """Validate GUI fields with Member 1's rules and read matching credentials."""
        email = email.strip()
        if not email or not password:
            raise ValueError("Email and password are required.")
        if not self.account_controller.validate_email(email):
            raise ValueError("Use an email address ending in @university.com.")
        if not self.account_controller.validate_password(password):
            raise ValueError("Start with an uppercase letter, use at least 5 letters, then at least 3 digits.")
        student = self.database.find_student_by_email(email)
        if student is None or student.password != password:
            raise ValueError("Invalid email or password.")
        return student

    def _latest_student(self, student):
        """Reject deleted accounts and load fresh enrolments before a GUI operation."""
        current = self.database.find_student_by_id(student.student_id)
        if current is None:
            raise ValueError("Student record not found. Please log in again.")
        return current

    def register_student(self, name, email, password, confirmation):
        """Create a Student using Member 1's validators and ID generator, then persist it."""
        name, email = name.strip(), email.strip()
        if not name or not email or not password or not confirmation:
            raise ValueError("Name, email, password and confirmation are required.")
        if not self.account_controller.validate_email(email):
            raise ValueError("Use an email address ending in @university.com.")
        if not self.account_controller.validate_password(password):
            raise ValueError("Start with an uppercase letter, use at least 5 letters, then at least 3 digits.")
        if password != confirmation:
            raise ValueError("Passwords do not match.")
        students = self.database.read_students()
        if any(student.email == email for student in students):
            raise ValueError("Student already exists. Sign in with this email instead.")
        student_id = self.account_controller.generate_student_id(students)
        student = Student(student_id, name, email, password)
        students.append(student)
        self.database.write_students(students)
        return student

    def view_enrolment(self, student):
        """Synchronise the GUI session with the original Student objects stored on disk."""
        current = self._latest_student(student)
        student.subjects = list(current.subjects)
        return list(student.subjects)

    def enrol_subject(self, student):
        """Call Member 2's enrolment method and translate its result into GUI data/errors."""
        current = self._latest_student(student)
        if len(current.subjects) >= 4:
            raise ValueError("You cannot enrol in more than four subjects.")
        previous_ids = {subject.subject_id for subject in current.subjects}
        previous_count = len(current.subjects)
        # Legacy methods print CLI messages; the GUI displays its own result views.
        with redirect_stdout(StringIO()):
            self.subject_controller.enrol_subject(current)
        updated = self._latest_student(student)
        additions = [subject for subject in updated.subjects if subject.subject_id not in previous_ids]
        if len(updated.subjects) != previous_count + 1 or len(additions) != 1:
            raise ValueError("Subject enrolment could not be saved. Please try again.")
        student.subjects = list(updated.subjects)
        return additions[0]

    def remove_subject(self, student, subject_id):
        """Remove a current enrolment using the model and update the session only after saving."""
        current = self._latest_student(student)
        selected = next((subject for subject in current.subjects if subject.subject_id == subject_id), None)
        if selected is None:
            raise ValueError("Subject is no longer enrolled. Refresh your subjects and try again.")
        previous_count = len(current.subjects)
        if not current.remove_subject(selected):
            raise ValueError("The selected subject could not be removed.")
        with redirect_stdout(StringIO()):
            self.subject_controller.save_student(current)
        updated = self._latest_student(student)
        if len(updated.subjects) != previous_count - 1 or any(subject.subject_id == subject_id for subject in updated.subjects):
            raise ValueError("Subject removal could not be saved. Please try again.")
        student.subjects = list(updated.subjects)
        return selected

    @staticmethod
    def summary(student):
        """Use Member 3's calculations to present the original model's current results."""
        average = AdminController.average_mark(student)
        grade = None if average is None else AdminController.grade_from_average(average)
        return {"count": len(student.subjects), "average": average, "grade": grade}
