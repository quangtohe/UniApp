"""Verify GUI registration preserves the original Student rules and shared file format."""

import pytest

from admin_gui_controller import AdminGUIController
from database import DatabaseError
from demo_data import DEMO_ADMIN_EMAIL, DEMO_ADMIN_PASSWORD
from gui_controller import GUIController
from student_controller import StudentController


@pytest.mark.parametrize("name,email,password,confirmation,message", (
    (" ", "new@university.com", "Abcde123", "Abcde123", "required"),
    ("New Student", "", "Abcde123", "Abcde123", "required"),
    ("New Student", "new@university.com", "", "", "required"),
    ("New Student", "new@university.com", "Abcde123", "", "required"),
    ("New Student", "new@gmail.com", "Abcde123", "Abcde123", "university.com"),
    ("New Student", "new@university.com", "abcde123", "abcde123", "uppercase"),
    ("New Student", "new@university.com", "Abcd123", "Abcd123", "5 letters"),
    ("New Student", "new@university.com", "Abcde12", "Abcde12", "3 digits"),
    ("New Student", "new@university.com", "Abcde123", "Abcde124", "do not match"),
))
def test_invalid_registration_does_not_write(database, name, email, password, confirmation, message):
    """Reject missing, malformed and unconfirmed fields before modifying the file."""
    before = database.filename.read_bytes()
    with pytest.raises(ValueError, match=message):
        GUIController(database).register_student(name, email, password, confirmation)
    assert database.filename.read_bytes() == before


def test_gui_registration_can_login_in_original_cli_and_appear_in_admin(database, student, monkeypatch):
    """Persist a compatible Student with a unique ID and share it with both subsystems."""
    service = GUIController(database)
    created = service.register_student("  New Student  ", "  new@university.com  ", "Abcde123", "Abcde123")
    assert created.name == "New Student" and created.email == "new@university.com"
    assert len(created.student_id) == 6 and created.student_id.isdigit()
    assert created.student_id != student.student_id and created.subjects == []
    assert len(database.read_students()) == 2
    answers = iter((created.email, "Abcde123"))
    monkeypatch.setattr("builtins.input", lambda prompt: next(answers))
    assert StudentController().login_student().student_id == created.student_id
    assert service.authenticate(created.email, "Abcde123").student_id == created.student_id
    admin = AdminGUIController(database, demo_mode=True)
    admin.authenticate(DEMO_ADMIN_EMAIL, DEMO_ADMIN_PASSWORD)
    assert admin.report()["summary"]["ungraded"] == 2
    with pytest.raises(ValueError, match="Invalid admin"):
        admin.authenticate(created.email, "Abcde123")


def test_duplicate_registration_preserves_existing_password_and_enrolments(database, student):
    """A repeated email must not replace a Student or discard their enrolled subjects."""
    service = GUIController(database)
    service.enrol_subject(student)
    before = database.filename.read_bytes()
    with pytest.raises(ValueError, match="already exists"):
        service.register_student("Replacement Name", student.email, "Other123", "Other123")
    assert database.filename.read_bytes() == before
    assert service.authenticate(student.email, student.password).subjects


def test_failed_registration_save_does_not_create_account(database, monkeypatch):
    """Propagate a write error without reporting that an account was successfully created."""
    def fail_save(students):
        """Simulate a file write failure before the snapshot can be persisted."""
        raise DatabaseError("Simulated registration write error")

    monkeypatch.setattr(database, "write_students", fail_save)
    with pytest.raises(DatabaseError, match="write error"):
        GUIController(database).register_student("New Student", "new@university.com", "Abcde123", "Abcde123")
    assert database.read_students() == []
