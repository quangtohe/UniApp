"""Authenticated Admin GUI adapter over the original admin rules and shared database."""

from dataclasses import dataclass
from hmac import compare_digest
import os

from admin_controller import AdminController
from database import Database
from demo_data import DEMO_ADMIN_EMAIL, DEMO_ADMIN_PASSWORD


@dataclass(frozen=True)
class AdminAccount:
    """Represent an administrator identity separately from Student model records."""

    email: str
    name: str


class AdminGUIController:
    """Require an admin session before reporting or modifying student records."""

    def __init__(self, database=None, demo_mode=False):
        """Use public demo credentials only in explicit demo mode, or configured credentials."""
        self.database = database if database is not None else Database()
        self.demo_mode = demo_mode
        self._email = DEMO_ADMIN_EMAIL if demo_mode else os.environ.get("UNIAPP_ADMIN_EMAIL", "")
        self._password = DEMO_ADMIN_PASSWORD if demo_mode else os.environ.get("UNIAPP_ADMIN_PASSWORD", "")
        self._account = None

    def authenticate(self, email, password):
        """Validate separate administrator credentials without looking in Student records."""
        self.logout()
        email = email.strip()
        if not email or not password:
            raise ValueError("Admin email and password are required.")
        if not self._email or not self._password:
            raise ValueError("Admin access is not configured. Use --demo to try the demo administrator.")
        ## if email.casefold() != self._email.casefold() or not compare_digest(password, self._password):
        if email.casefold() != self._email.casefold() or not compare_digest(password.encode("utf-8"), self._password.encode("utf-8")):
            raise ValueError("Invalid admin email or password.")
        self._account = AdminAccount(self._email, "Demo Administrator" if self.demo_mode else "Administrator")
        return self._account

    def logout(self):
        """Revoke the current administrator session."""
        self._account = None

    def _require_admin(self):
        """Reject every reporting and mutation request made without admin authentication."""
        if self._account is None:
            raise PermissionError("Please sign in as an administrator.")

    def report(self, mode="all", query=""):
        """Read one snapshot, reuse Member 3's averages, and organise rows for the view."""
        self._require_admin()
        students = self.database.read_students()
        rows = []
        summary = {"students": len(students), "enrolments": 0, "passed": 0, "failed": 0, "ungraded": 0}
        for student in students:
            average = AdminController.average_mark(student)
            grade = None if average is None else AdminController.grade_from_average(average)
            outcome = "NOT GRADED" if average is None else "PASS" if average >= 50 else "FAIL"
            summary["enrolments"] += len(student.subjects)
            summary[{"PASS": "passed", "FAIL": "failed", "NOT GRADED": "ungraded"}[outcome]] += 1
            rows.append({"student_id": student.student_id, "name": student.name, "email": student.email,
                         "subjects": len(student.subjects), "average": average, "grade": grade, "outcome": outcome})
        query = query.strip().casefold()
        if query:
            rows = [row for row in rows if any(query in str(row[field]).casefold() for field in ("student_id", "name", "email"))]
        if mode == "grade":
            order = {"HD": 0, "D": 1, "C": 2, "P": 3, "Z": 4, None: 5}
            rows.sort(key=lambda row: (order[row["grade"]], row["student_id"]))
        elif mode == "pass_fail":
            order = {"PASS": 0, "FAIL": 1, "NOT GRADED": 2}
            rows.sort(key=lambda row: (order[row["outcome"]], row["student_id"]))
        elif mode == "all":
            rows.sort(key=lambda row: row["student_id"])
        else:
            raise ValueError("Unknown student report view.")
        return {"rows": rows, "summary": summary}

    def remove_student(self, student_id):
        """Remove exactly one selected account and its owned enrolments after UI confirmation."""
        self._require_admin()
        students = self.database.read_students()
        remaining = [student for student in students if student.student_id != student_id]
        if len(remaining) == len(students):
            raise ValueError("Student record not found. Refresh the list and try again.")
        self.database.write_students(remaining)

    def clear_students(self, confirmation):
        """Clear the shared file only for an authenticated admin supplying the exact phrase."""
        self._require_admin()
        if confirmation != "CLEAR":
            raise ValueError("Type CLEAR to confirm removal of all student records.")
        self.database.clear_students()
