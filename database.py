"""Member 4: shared pickle persistence compatible with the original group models."""

import os
import pickle
import tempfile
from pathlib import Path

from student import Student
from subject import Subject


class DatabaseError(Exception):
    """Report unreadable or unwritable storage without silently discarding records."""


class StudentUnpickler(pickle.Unpickler):
    """Read only the two original model classes stored in the group's data file."""

    def find_class(self, module, name):
        """Reject unexpected executable classes while retaining old pickle compatibility."""
        allowed = {("student", "Student"): Student, ("subject", "Subject"): Subject}
        if (module, name) not in allowed:
            raise pickle.UnpicklingError("Unexpected object in student database.")
        return allowed[(module, name)]


class Database:
    """Create, read, write, search and clear one shared student-record file."""

    _default_filename = None

    @classmethod
    def configure_default(cls, filename=None):
        """Route legacy controllers' Database() calls to the file selected at startup."""
        cls._default_filename = None if filename is None else Path(filename).resolve()

    def __init__(self, filename=None):
        """Accept a custom file while keeping Database() compatible with Members 1-3."""
        selected = filename if filename is not None else self._default_filename
        self.filename = Path(selected).resolve() if selected is not None else Path(__file__).with_name("students.data")
        self.create_file()

    def create_file(self):
        """Create a missing file; preserve empty or corrupt existing files for diagnosis."""
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
    def _validate_records(students):
        """Require Student objects with subject lists while leaving business rules to models."""
        if not isinstance(students, list) or any(not isinstance(student, Student) for student in students):
            raise ValueError("Database must contain a list of Student objects.")
        for student in students:
            if not all(hasattr(student, field) for field in ("student_id", "name", "email", "password", "subjects")):
                raise ValueError("Incomplete student record.")
            if not isinstance(student.subjects, list) or any(not isinstance(subject, Subject) for subject in student.subjects):
                raise ValueError("Invalid subject list in student record.")

    def read_students(self):
        """Load original Student/Subject objects and report storage or format errors."""
        try:
            with self.filename.open("rb") as stream:
                students = StudentUnpickler(stream).load()
            self._validate_records(students)
            return students
        except (OSError, pickle.PickleError, EOFError, ValueError, TypeError, AttributeError) as error:
            raise DatabaseError(f"Cannot read {self.filename.name}; original data preserved: {error}") from error

    def write_students(self, students):
        """Save a complete temporary snapshot before atomically replacing the data file."""
        temporary = None
        try:
            self._validate_records(students)
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

    def find_student_by_id(self, student_id):
        """Read the latest student matching an exact ID, or return None."""
        return next((student for student in self.read_students() if student.student_id == student_id), None)

    def find_student_by_email(self, email):
        """Use the same exact email comparison as the original StudentController."""
        return next((student for student in self.read_students() if student.email == email), None)

    def clear_students(self):
        """Persist an empty list after the calling admin menu obtains confirmation."""
        self.write_students([])


## ORIGINAL CODE - retained as requested; Member 4 implementation appears above.
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
