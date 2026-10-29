"""Verify the portable demo account, persistence and CLI/GUI startup configuration."""

import pytest
from unittest.mock import Mock

import main as entry_point
from demo_data import DEMO_EMAIL, DEMO_PASSWORD, create_demo_database
from student_controller import StudentController
from subject_controller import SubjectController


def test_fresh_demo_has_working_credentials(tmp_path):
    """A new demo database must support the documented login without manual setup."""
    database = create_demo_database(tmp_path / "demo.data")
    student = StudentController(database).authenticate(DEMO_EMAIL, DEMO_PASSWORD)
    assert student.name == "Demo Student"
    assert student.subjects == []


def test_reopening_demo_keeps_enrolments_without_duplicate_accounts(tmp_path):
    """Starting demo mode again must keep subjects and create only one demo account."""
    path = tmp_path / "demo.data"
    database = create_demo_database(path)
    student = StudentController(database).authenticate(DEMO_EMAIL, DEMO_PASSWORD)
    enrolled = SubjectController(database).enrol_subject(student)
    reopened = create_demo_database(path)
    assert len(reopened.read_students()) == 1
    assert reopened.read_students()[0].subjects[0].subject_id == enrolled.subject_id


def test_demo_restores_public_password_and_preserves_other_accounts(tmp_path):
    """Keep demo login predictable after password changes while retaining every record."""
    path = tmp_path / "demo.data"
    database = create_demo_database(path)
    accounts = StudentController(database)
    demo = accounts.authenticate(DEMO_EMAIL, DEMO_PASSWORD)
    SubjectController(database).change_password(demo, "Newpass456")
    accounts.register("Other Student", "other@university.com", "Otherpass123")
    reopened = create_demo_database(path)
    accounts = StudentController(reopened)
    assert accounts.authenticate(DEMO_EMAIL, DEMO_PASSWORD).student_id == demo.student_id
    assert accounts.authenticate("other@university.com", "Otherpass123").name == "Other Student"
    assert len(reopened.read_students()) == 2


def test_demo_and_custom_data_are_mutually_exclusive(tmp_path):
    """Reject ambiguous command-line options before creating any database."""
    path = tmp_path / "custom.data"
    with pytest.raises(SystemExit) as error:
        entry_point.main(["--demo", "--data", str(path)])
    assert error.value.code == 2
    assert not path.exists()


## def test_gui_demo_prefills_valid_credentials(tmp_path, monkeypatch):
##     """Exercise the real entry point and authentication without entering a Tk mainloop."""
##     database = create_demo_database(tmp_path / "demo.data")
##     monkeypatch.setattr(entry_point, "create_demo_database", lambda: database)
##     from gui_uni_app import GUIUniApp
##
##     def check_prefilled_login(application):
##         """Verify the GUI received the demo file and valid prefilled login fields."""
##         try:
##             assert application.database.filename == database.filename
##             assert application.email_var.get() == DEMO_EMAIL
##             assert application.password_var.get() == DEMO_PASSWORD
##             student = application.student_system.authenticate(application.email_var.get(), application.password_var.get())
##             assert student.name == "Demo Student"
##         finally:
##             application.close()
##
##     monkeypatch.setattr(GUIUniApp, "run", check_prefilled_login)
##     assert entry_point.main(["--gui", "--demo"]) == 0


def test_gui_demo_prefills_valid_credentials(tmp_path, monkeypatch):
    """Check entry-point wiring without creating a second Tcl interpreter in GUI tests."""
    database = create_demo_database(tmp_path / "demo.data")
    monkeypatch.setattr(entry_point, "create_demo_database", lambda: database)
    import gui_uni_app

    application = Mock()
    factory = Mock(return_value=application)
    monkeypatch.setattr(gui_uni_app, "GUIUniApp", factory)
    assert entry_point.main(["--gui", "--demo"]) == 0
    factory.assert_called_once_with(database=database)
    email = application.email_var.set.call_args.args[0]
    password = application.password_var.set.call_args.args[0]
    assert StudentController(database).authenticate(email, password).name == "Demo Student"
    application.run.assert_called_once_with()
