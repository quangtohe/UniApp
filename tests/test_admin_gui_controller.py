"""Test separate admin authentication and persisted reporting without desktop windows."""

import pytest

from admin_gui_controller import AdminGUIController
from demo_data import DEMO_ADMIN_EMAIL, DEMO_ADMIN_PASSWORD, DEMO_EMAIL, DEMO_PASSWORD
from gui_controller import GUIController
from student import Student
from subject import Subject


@pytest.fixture
def admin(database):
    """Authenticate a demo administrator against an isolated test database."""
    service = AdminGUIController(database, demo_mode=True)
    service.authenticate(DEMO_ADMIN_EMAIL, DEMO_ADMIN_PASSWORD)
    return service


@pytest.fixture
def records(database):
    """Persist students at grading boundaries, including one without enrolments."""
    students = []
    for index, mark in enumerate((85, 75, 65, 50, 49, None), 1):
        student = Student(f"{index:06d}", f"Student {index}", f"person{index}@university.com", "Abcde123")
        if mark is not None:
            subject = Subject()
            subject.mark = mark
            subject.grade = subject.calculate_grade()
            student.subjects.append(subject)
        students.append(student)
    database.write_students(students)
    return students


@pytest.mark.parametrize("operation", ("report", "remove", "clear"))
def test_admin_operations_require_authentication(database, student, operation):
    """Each public data operation must reject a caller without an admin session."""
    service = AdminGUIController(database, demo_mode=True)
    with pytest.raises(PermissionError):
        if operation == "report":
            service.report()
        elif operation == "remove":
            service.remove_student(student.student_id)
        else:
            service.clear_students("CLEAR")
    assert database.find_student_by_id(student.student_id) is not None


@pytest.mark.parametrize("email,password", (("", ""), (DEMO_EMAIL, DEMO_PASSWORD), (DEMO_ADMIN_EMAIL, "Wrong123"), (DEMO_ADMIN_EMAIL, "mậtkhẩu")))
def test_invalid_admin_login_revokes_existing_session(admin, email, password):
    """Wrong credentials, including Unicode input, produce a normal validation error."""
    with pytest.raises(ValueError):
        admin.authenticate(email, password)
    with pytest.raises(PermissionError):
        admin.report()


def test_admin_identity_is_not_a_student_record(admin, database, student):
    """Admin authentication must not create an enrolment account or allow student login."""
    account = admin.authenticate(f" {DEMO_ADMIN_EMAIL.upper()} ", DEMO_ADMIN_PASSWORD)
    assert account.name == "Demo Administrator"
    assert database.read_students()[0].student_id == student.student_id
    assert database.find_student_by_email(DEMO_ADMIN_EMAIL) is None
    with pytest.raises(ValueError):
        GUIController(database).authenticate(DEMO_ADMIN_EMAIL, DEMO_ADMIN_PASSWORD)
    admin.logout()
    with pytest.raises(PermissionError):
        admin.report()


def test_normal_mode_requires_explicit_admin_configuration(database, monkeypatch):
    """Public demo credentials must not open a normal installation's database."""
    monkeypatch.delenv("UNIAPP_ADMIN_EMAIL", raising=False)
    monkeypatch.delenv("UNIAPP_ADMIN_PASSWORD", raising=False)
    service = AdminGUIController(database)
    with pytest.raises(ValueError, match="not configured"):
        service.authenticate(DEMO_ADMIN_EMAIL, DEMO_ADMIN_PASSWORD)
    monkeypatch.setenv("UNIAPP_ADMIN_EMAIL", "owner@university.com")
    monkeypatch.setenv("UNIAPP_ADMIN_PASSWORD", "Owner123")
    service = AdminGUIController(database)
    with pytest.raises(ValueError, match="Invalid"):
        service.authenticate(DEMO_ADMIN_EMAIL, DEMO_ADMIN_PASSWORD)
    assert service.authenticate("owner@university.com", "Owner123").name == "Administrator"
    assert service.report()["summary"]["students"] == 0


def test_grade_and_pass_fail_reports_use_existing_rules(admin, records):
    """Boundary grades and the ungraded state must match Member 3's calculations."""
    report = admin.report("grade")
    assert [row["grade"] for row in report["rows"]] == ["HD", "D", "C", "P", "Z", None]
    assert report["summary"] == {"students": 6, "enrolments": 5, "passed": 4, "failed": 1, "ungraded": 1}
    assert [row["outcome"] for row in admin.report("pass_fail")["rows"]] == ["PASS"] * 4 + ["FAIL", "NOT GRADED"]
    with pytest.raises(ValueError, match="Unknown"):
        admin.report("invalid")


@pytest.mark.parametrize("query", ("  STUDENT 2 ", "person2@", "000002"))
def test_search_matches_name_email_or_id_without_changing_totals(admin, records, query):
    """Search is case insensitive and keeps the overall metric counts intact."""
    report = admin.report(query=query)
    assert [row["student_id"] for row in report["rows"]] == ["000002"]
    assert report["summary"]["students"] == 6


def test_remove_preserves_other_records_and_reads_fresh_state(admin, records, database):
    """Deletion removes only the chosen account and subsequent reports read the file."""
    admin.remove_student("000002")
    assert [s.student_id for s in database.read_students()] == ["000001", "000003", "000004", "000005", "000006"]
    assert len(database.read_students()[0].subjects) == 1
    assert admin.report()["summary"]["students"] == 5
    before = database.filename.read_bytes()
    with pytest.raises(ValueError, match="not found"):
        admin.remove_student("000002")
    assert database.filename.read_bytes() == before


def test_clear_requires_exact_phrase(admin, records, database):
    """An incorrect confirmation cannot modify the persisted records."""
    for phrase in ("", "clear", "CLEAR "):
        with pytest.raises(ValueError, match="CLEAR"):
            admin.clear_students(phrase)
    assert len(database.read_students()) == 6
    admin.clear_students("CLEAR")
    assert database.read_students() == []


def test_admin_entry_point_selects_role_and_prefills_separate_account(database, monkeypatch):
    """The actual CLI flag must select Admin and supply only the Admin demo credentials."""
    from unittest.mock import Mock
    import main
    import gui_uni_app

    monkeypatch.setattr(main, "create_demo_database", lambda: database)
    application = Mock()
    monkeypatch.setattr(gui_uni_app, "GUIUniApp", Mock(return_value=application))
    assert main.main(["--gui", "--admin", "--demo"]) == 0
    application.set_login_role.assert_called_once_with("admin")
    application.email_var.set.assert_called_once_with(DEMO_ADMIN_EMAIL)
    application.password_var.set.assert_called_once_with(DEMO_ADMIN_PASSWORD)


def test_admin_flag_without_gui_is_rejected_before_file_creation(tmp_path):
    """Reject a GUI-only role option when starting the legacy CLI."""
    import main

    path = tmp_path / "unused.data"
    with pytest.raises(SystemExit) as error:
        main.main(["--admin", "--data", str(path)])
    assert error.value.code == 2 and not path.exists()
