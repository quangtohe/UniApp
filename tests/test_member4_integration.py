"""Test Member 4 persistence, university navigation and original-controller integration."""

import pickle
import subprocess
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

from admin_controller import AdminController
from database import Database, DatabaseError
from demo_data import DEMO_EMAIL, DEMO_PASSWORD, create_demo_database
from gui_controller import GUIController
from student_controller import StudentController
from subject import Subject
from subject_controller import SubjectController


def test_database_creates_file_and_roundtrips_original_models(database, student):
    """Persist actual Student/Subject objects, then read them through a new Database."""
    subject = Subject()
    assert student.enrol_subject(subject)
    database.write_students([student])
    reopened = Database(database.filename)
    loaded = reopened.find_student_by_id(student.student_id)
    assert loaded.name == "Test Student"
    assert loaded.subjects[0].subject_id == subject.subject_id
    assert loaded.subjects[0].mark == subject.mark
    assert loaded.subjects[0].grade == subject.grade


def test_custom_file_is_shared_by_legacy_controllers(database):
    """Nested student, subject and admin constructors must use the selected file."""
    assert StudentController().database.filename == database.filename
    assert SubjectController().database.filename == database.filename
    assert AdminController().database.filename == database.filename


def test_database_reads_legacy_pickle(database, student):
    """Accept the original pickle object layout without a data migration."""
    database.filename.write_bytes(pickle.dumps([student], protocol=4))
    loaded = Database(database.filename).read_students()[0]
    assert loaded.email == student.email and loaded.password == student.password


@pytest.mark.parametrize("content", [b"", b"invalid pickle", pickle.dumps({"unexpected": "shape"})])
def test_corrupt_data_is_reported_and_preserved(database, content):
    """A malformed file must raise an error instead of being reset to an empty list."""
    database.filename.write_bytes(content)
    with pytest.raises(DatabaseError):
        Database(database.filename).read_students()
    assert database.filename.read_bytes() == content


def test_unexpected_pickle_class_is_rejected(database):
    """Reject a pickle containing objects outside the group's Student/Subject models."""
    database.filename.write_bytes(pickle.dumps(Path("unexpected")))
    with pytest.raises(DatabaseError, match="Unexpected object"):
        database.read_students()


def test_atomic_save_failure_preserves_original_file(database, student, monkeypatch):
    """A failed final file replacement must preserve the previous complete snapshot."""
    original = database.filename.read_bytes()

    def fail_replace(source, target):
        """Simulate the target file being locked while saving."""
        raise OSError("Simulated locked file")

    monkeypatch.setattr("database.os.replace", fail_replace)
    with pytest.raises(DatabaseError):
        database.write_students([])
    assert database.filename.read_bytes() == original
    assert list(database.filename.parent.iterdir()) == [database.filename]


def test_gui_authenticates_account_registered_by_member1(database, student):
    """The GUI must read an account created by the unmodified CLI registration code."""
    authenticated = GUIController(database).authenticate(student.email, student.password)
    assert authenticated.student_id == student.student_id


@pytest.mark.parametrize("email,password,message", [("", "Abcde123", "required"), ("test@university.com", "", "required"), ("test@example.com", "Abcde123", "university.com"), ("test@university.com", "bad", "uppercase"), ("test@university.com", "Wrong123", "Invalid email or password"), ("unknown@university.com", "Abcde123", "Invalid email or password")])
def test_gui_login_reports_invalid_inputs(database, student, email, password, message):
    """Translate field/format/authentication failures into readable GUI errors."""
    with pytest.raises(ValueError, match=message):
        GUIController(database).authenticate(email, password)


def test_gui_enrolment_reuses_member2_and_persists_four_subjects(database, student):
    """Enrol through the original SubjectController, rejecting a fifth stale-session call."""
    service = GUIController(database)
    stale = database.find_student_by_id(student.student_id)
    for _ in range(4):
        subject = service.enrol_subject(student)
        assert 1 <= subject.subject_id <= 999 and 25 <= subject.mark <= 100
    original = database.filename.read_bytes()
    with pytest.raises(ValueError, match="four"):
        service.enrol_subject(stale)
    assert database.filename.read_bytes() == original
    assert len(Database(database.filename).read_students()[0].subjects) == 4


def test_gui_refresh_observes_legacy_cli_enrolment(database, student):
    """The GUI must reload subjects saved through Member 2's original controller."""
    service = GUIController(database)
    gui_student = service.authenticate(student.email, student.password)
    SubjectController().enrol_subject(student)
    subjects = service.view_enrolment(gui_student)
    assert len(subjects) == 1 and len(gui_student.subjects) == 1


def test_gui_average_uses_member3_calculations(database, student):
    """Display the same average/grade as the admin system for the original model."""
    for mark in (60, 65, 70, 78):
        subject = Subject()
        subject.mark = mark
        subject.grade = subject.calculate_grade()
        student.subjects.append(subject)
    summary = GUIController(database).summary(student)
    assert summary == {"count": 4, "average": 68.25, "grade": "C"}


def test_deleted_account_cannot_continue_using_gui(database, student, monkeypatch):
    """Admin deletion through Member 3's menu must invalidate an old GUI session."""
    service = GUIController(database)
    responses = iter((student.student_id, "y"))
    monkeypatch.setattr("builtins.input", lambda prompt: next(responses))
    AdminController().remove_student()
    with pytest.raises(ValueError, match="not found"):
        service.enrol_subject(student)


def test_failed_enrol_save_keeps_gui_session_unchanged(database, student, monkeypatch):
    """Do not update the GUI's copy when the legacy enrolment cannot be persisted."""
    service = GUIController(database)

    def fail_write(students):
        """Simulate storage failing while a subject is being enrolled."""
        raise DatabaseError("Simulated storage error")

    monkeypatch.setattr(database, "write_students", fail_write)
    with pytest.raises(DatabaseError):
        service.enrol_subject(student)
    assert student.subjects == [] and database.read_students()[0].subjects == []


def test_clear_removes_objects_persistently(database, student):
    """Clearing records must leave an empty readable file for every subsystem."""
    database.clear_students()
    assert Database(database.filename).read_students() == []


def test_complete_cli_navigation_and_legacy_enrolment(tmp_path):
    """Run the actual menus via stdin using original register, subject and admin options."""
    path = tmp_path / "cli.data"
    commands = "\n".join(("S", "r", "CLI Student", "cli@university.com", "Abcde123", "l", "cli@university.com", "Abcde123", "1", "2", "5", "x", "A", "1", "6", "X", ""))
    result = subprocess.run([sys.executable, "main.py", "--data", str(path)], input=commands, text=True, capture_output=True, cwd=Path(__file__).resolve().parents[1], timeout=15)
    assert result.returncode == 0, result.stderr
    for expected in ("University System", "Registration successful", "Login successful", "Subject enrolled successfully", "Total students: 1", "Thank You"):
        assert expected in result.stdout
    assert len(Database(path).read_students()[0].subjects) == 1


def test_university_handles_invalid_selection_and_menu_returns(tmp_path):
    """Returning from either original subsystem must lead back to University Menu."""
    path = tmp_path / "menus.data"
    result = subprocess.run([sys.executable, "main.py", "--data", str(path)], input="bad\nS\nx\nA\n6\nX\n", text=True, capture_output=True, cwd=Path(__file__).resolve().parents[1], timeout=15)
    assert result.returncode == 0
    assert "Invalid option" in result.stdout
    assert result.stdout.count("University System:") == 4
    assert Database(path).read_students() == []


def test_demo_login_is_portable_and_preserves_enrolments(tmp_path, monkeypatch):
    """A new demo file works immediately and opening it again keeps the enrolled subjects."""
    monkeypatch.setattr(Database, "_default_filename", None)
    path = tmp_path / "demo.data"
    database = create_demo_database(path)
    service = GUIController(database)
    student = service.authenticate(DEMO_EMAIL, DEMO_PASSWORD)
    service.enrol_subject(student)
    reopened = create_demo_database(path)
    assert len(reopened.read_students()) == 1
    assert len(GUIController(reopened).authenticate(DEMO_EMAIL, DEMO_PASSWORD).subjects) == 1


def test_demo_entry_point_prefills_gui_without_extra_tk_root(database, monkeypatch):
    """Verify --demo wiring separately from the real GUI's single-interpreter tests."""
    import main
    import gui_uni_app

    demo = create_demo_database(database.filename)
    monkeypatch.setattr(main, "create_demo_database", lambda: demo)
    application = Mock()
    factory = Mock(return_value=application)
    monkeypatch.setattr(gui_uni_app, "GUIUniApp", factory)
    assert main.main(["--gui", "--demo"]) == 0
    ## factory.assert_called_once_with(database=demo)
    factory.assert_called_once_with(database=demo, demo_mode=True)
    email = application.email_var.set.call_args.args[0]
    password = application.password_var.set.call_args.args[0]
    assert GUIController(demo).authenticate(email, password).name == "Demo Student"


def test_conflicting_data_arguments_do_not_create_file(tmp_path):
    """Reject ambiguous --demo/--data options before any persistence is initialised."""
    import main

    path = tmp_path / "unused.data"
    with pytest.raises(SystemExit) as error:
        main.main(["--demo", "--data", str(path)])
    assert error.value.code == 2 and not path.exists()
