"""Read and atomically save the group's existing students.data pickle format."""

import os
import pickle
import tempfile
from pathlib import Path

from grade import Grade
from student import Student
from subject import Subject


class DatabaseError(Exception):
    """Report storage problems without silently replacing the original records."""


class StudentUnpickler(pickle.Unpickler):
    """Load only the model classes used by this application and its legacy data."""

    def find_class(self, module, name):
        """Reject arbitrary executable objects in an unexpected pickle file."""
        allowed = {("student", "Student"): Student, ("subject", "Subject"): Subject,
                   ("grade", "Grade"): Grade}
        if (module, name) not in allowed:
            raise pickle.UnpicklingError("Unexpected object in students.data.")
        return allowed[(module, name)]


class Database:
    """Manage one file shared by CLI and GUI; accept a temporary path for tests."""

    def __init__(self, filename=None):
        """Use the project data file by default and create only missing files."""
        self.filename = Path(filename) if filename is not None else Path(__file__).with_name("students.data")
        self.create_file()

    def create_file(self):
        """Initialise a missing database without overwriting an empty/corrupt file."""
        try:
            self.filename.parent.mkdir(parents=True, exist_ok=True)
            if not self.filename.exists():
                with self.filename.open("xb") as stream:
                    pickle.dump([], stream)
        except FileExistsError:
            pass
        except OSError as error:
            raise DatabaseError(f"Cannot create database: {error}") from error

    @staticmethod
    def _validate_students(students):
        """Check record shape and identifiers while allowing legacy string grades."""
        if not isinstance(students, list):
            raise ValueError("Expected a list of student records.")
        ids, emails = set(), set()
        for student in students:
            if not isinstance(student, Student):
                raise ValueError("Unexpected student record.")
            if not isinstance(student.student_id, str) or len(student.student_id) != 6 or not student.student_id.isascii() or not student.student_id.isdigit() or int(student.student_id) == 0:
                raise ValueError("Invalid six-digit student ID.")
            if not all(isinstance(value, str) and value.strip() for value in (student.name, student.email, student.password)):
                raise ValueError("Invalid student fields.")
            if student.student_id in ids or student.email.lower() in emails:
                raise ValueError("Duplicate student ID or email.")
            ids.add(student.student_id)
            emails.add(student.email.lower())
            if not isinstance(student.subjects, list) or len(student.subjects) > Student.MAX_SUBJECTS:
                raise ValueError("Invalid enrolment list.")
            subject_ids = set()
            for subject in student.subjects:
                if not isinstance(subject, Subject) or type(subject.subject_id) is not int or not 1 <= subject.subject_id <= 999:
                    raise ValueError("Invalid subject record.")
                if subject.subject_id in subject_ids or type(subject.mark) is not int or not 25 <= subject.mark <= 100 or subject.grade != Grade.from_mark(subject.mark):
                    raise ValueError("Invalid subject mark, grade or duplicate ID.")
                subject_ids.add(subject.subject_id)

    def read_students(self):
        """Load compatible student objects and report unreadable data explicitly."""
        try:
            with self.filename.open("rb") as stream:
                students = StudentUnpickler(stream).load()
            self._validate_students(students)
            return students
        except (OSError, pickle.PickleError, EOFError, ValueError, TypeError, AttributeError) as error:
            raise DatabaseError(f"Cannot read {self.filename.name}; original data preserved: {error}") from error

    def write_students(self, students):
        """Write a complete validated snapshot before atomically replacing the file."""
        temporary = None
        try:
            self._validate_students(students)
            with tempfile.NamedTemporaryFile(mode="wb", dir=self.filename.parent, delete=False) as stream:
                temporary = Path(stream.name)
                pickle.dump(students, stream, protocol=pickle.HIGHEST_PROTOCOL)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.filename)
        except (OSError, pickle.PickleError, ValueError, TypeError, AttributeError) as error:
            raise DatabaseError(f"Cannot save students: {error}") from error
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink()

    def find_student_by_email(self, email):
        """Find an account case-insensitively to prevent duplicate login identities."""
        return next((student for student in self.read_students() if student.email.lower() == email.lower()), None)

    def find_student_by_id(self, student_id):
        """Find a student by the exact persisted six-digit ID."""
        return next((student for student in self.read_students() if student.student_id == student_id), None)

    def clear_students(self):
        """Save an empty list after the caller has obtained deletion confirmation."""
        self.write_students([])


## ORIGINAL CODE - retained as requested; active implementation appears above.
## import os
## import pickle
## 
## class Database:
##     def __init__(self):
##         current_folder = os.path.dirname(__file__)
##         self.filename = os.path.join(current_folder, "students.data")
##         self.create_file()
## 
##     def create_file(self):
##         if not os.path.exists(self.filename) or os.path.getsize(self.filename) == 0:
##             with open(self.filename, "wb") as file:
##                 pickle.dump([], file)
## 
##     def read_students(self):
##         with open(self.filename, "rb") as file:
##             return pickle.load(file)
## 
##     def write_students(self, students):
##         with open(self.filename, "wb") as file:
##             pickle.dump(students, file)
## 
##     def clear_students(self):
##         self.write_students([])
