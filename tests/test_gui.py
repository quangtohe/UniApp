"""Exercise all four real Tk windows without displaying test windows or using real data."""

import tkinter as tk

import pytest

from gui_uni_app import GUIUniApp, EnrolmentWindow, ExceptionWindow, SubjectWindow
from subject_controller import SubjectController


## @pytest.fixture
## def gui(database):
##     """Build actual Tk widgets in hidden mode and destroy them after each test."""
##     try:
##         root = tk.Tk()
##     except tk.TclError as error:
##         pytest.skip(f"Tk display unavailable: {error}")
##     app = GUIUniApp(root=root, database=database, visible=False)
##     yield app
##     app.close()


@pytest.fixture(scope="module")
def tk_root():
    """Use one Tcl/Tk interpreter, matching the application's one-root lifecycle."""
    try:
        root = tk.Tk()
    except tk.TclError as error:
        if "no display name" in str(error) or "couldn't connect to display" in str(error):
            pytest.skip(f"Tk display unavailable: {error}")
        raise
    root.withdraw()
    yield root
    root.destroy()


@pytest.fixture
def gui(database, tk_root):
    """Give each test isolated data and fresh views on the shared hidden root."""
    app = GUIUniApp(root=tk_root, database=database, visible=False)
    yield app
    app.show_login_window()
    app.login_view.destroy()
    tk_root.unbind("<Return>")


def login_student(gui, student):
    """Fill the login view and activate its real login button."""
    gui.email_var.set(student.email)
    gui.password_var.set("Abcde123")
    gui.login_button.invoke()
    assert gui.current_student.student_id == student.student_id


def test_gui_empty_invalid_and_wrong_credentials(gui, student):
    """Show the dedicated exception window for every required invalid-login case."""
    assert not gui.login()
    assert isinstance(gui.exception_window, ExceptionWindow)
    assert "required" in gui.exception_window.message_var.get()
    gui.exception_window.ok_button.invoke()
    assert gui.exception_window is None
    gui.email_var.set("invalid")
    gui.password_var.set("Abcde123")
    assert not gui.login()
    assert "university.com" in gui.exception_window.message_var.get()
    gui.email_var.set(student.email)
    gui.password_var.set("Wrong123")
    assert not gui.login()
    assert "Invalid email or password" in gui.exception_window.message_var.get()
    assert gui.current_student is None


def test_gui_four_distinct_windows_and_fifth_enrol_attempt(gui, student, database):
    """Verify login root, enrolment, subjects and error are four separate window objects."""
    login_student(gui, student)
    assert isinstance(gui.enrolment_window, EnrolmentWindow)
    gui.enrolment_window.subjects_button.invoke()
    assert isinstance(gui.subject_window, SubjectWindow)
    for _ in range(4):
        gui.enrol_button.invoke()
    assert len(gui.subject_table.get_children()) == 4
    assert "4/4" in gui.count_var.get()
    assert "Average:" in gui.enrolment_window.average_var.get()
    gui.enrol_button.invoke()
    assert isinstance(gui.exception_window, ExceptionWindow)
    assert "four" in gui.exception_window.message_var.get()
    windows = (gui.root, gui.enrolment_window, gui.subject_window, gui.exception_window)
    assert len({str(window) for window in windows}) == 4
    assert all(window.winfo_exists() for window in windows)
    assert len(database.read_students()[0].subjects) == 4


def test_gui_logout_relogin_and_subject_window_reopen(gui, student):
    """Closing subjects retains login; logout discards every child and clears credentials."""
    login_student(gui, student)
    gui.enrol_button.invoke()
    gui.show_subject_window()
    old = gui.subject_window
    gui.close_subject_window()
    assert not old.winfo_exists() and gui.current_student is not None
    assert gui.show_subject_window()
    assert len(gui.subject_table.get_children()) == 1
    gui.enrolment_window.logout_button.invoke()
    assert gui.current_student is None
    assert gui.enrolment_window is None and gui.subject_window is None
    assert gui.email_var.get() == "" and gui.password_var.get() == ""
    login_student(gui, student)
    gui.show_subject_window()
    assert len(gui.subject_table.get_children()) == 1


def test_gui_and_cli_share_enrolments(gui, student):
    """Refreshing the subject window must reflect changes made through CLI services."""
    login_student(gui, student)
    gui.show_subject_window()
    assert "No subjects" in gui.subject_window.status_var.get()
    SubjectController(gui.database).enrol_subject(student)
    assert gui.refresh_subjects()
    assert len(gui.subject_table.get_children()) == 1


def test_gui_deleted_account_returns_to_login(gui, student):
    """A removed account returns to login and sees an exception window explaining why."""
    login_student(gui, student)
    gui.show_subject_window()
    gui.database.clear_students()
    assert not gui.refresh_subjects()
    assert gui.current_student is None and gui.enrolment_window is None
    assert isinstance(gui.exception_window, ExceptionWindow)
    assert "not found" in gui.exception_window.message_var.get()


## PRE-CANVAS IMPLEMENTATION - retained as ## comments before course-aligned changes.
## """Run actual Tk widgets against isolated persistence without displaying test windows."""
## 
## import tkinter as tk
## 
## import pytest
## 
## from gui_uni_app import GUIUniApp
## from subject_controller import SubjectController
## 
## 
## @pytest.fixture
## def gui(database, monkeypatch):
##     """Create a hidden real Tk window and capture modal errors for assertions."""
##     try:
##         root = tk.Tk()
##     except tk.TclError as error:
##         pytest.skip(f"Tk display unavailable: {error}")
##     root.withdraw()
##     app = GUIUniApp(root=root, database=database)
##     app.errors = []
##     monkeypatch.setattr(app, "display_error", app.errors.append)
##     yield app
##     root.destroy()
## 
## 
## def test_gui_empty_invalid_and_wrong_credentials(gui, student):
##     """Reject blank, malformed and unmatched credentials with no logged-in student."""
##     assert not gui.login()
##     gui.email_var.set("invalid")
##     gui.password_var.set("Abcde123")
##     assert not gui.login()
##     gui.email_var.set(student.email)
##     gui.password_var.set("Wrong123")
##     assert not gui.login()
##     assert len(gui.errors) == 3 and gui.current_student is None
## 
## 
## def test_gui_login_enrol_limit_logout_and_relogin(gui, student, database):
##     """Use real button callbacks to persist four subjects and disable a fifth enrolment."""
##     gui.email_var.set(student.email)
##     gui.password_var.set("Abcde123")
##     gui.login_button.invoke()
##     assert gui.current_student.student_id == student.student_id
##     for _ in range(4):
##         gui.enrol_button.invoke()
##     assert len(gui.subject_table.get_children()) == 4
##     assert str(gui.enrol_button.cget("state")) == "disabled"
##     assert not gui.enrol_in_subject()
##     assert "four" in gui.errors[-1]
##     assert len(database.read_students()[0].subjects) == 4
##     gui.show_login_window()
##     assert gui.current_student is None and gui.password_var.get() == ""
##     gui.email_var.set(student.email)
##     gui.password_var.set("Abcde123")
##     assert gui.login()
##     assert len(gui.subject_table.get_children()) == 4
## 
## 
## def test_gui_and_cli_share_enrolments(gui, student):
##     """Refresh in the GUI must display enrolments made through the CLI service."""
##     gui.email_var.set(student.email)
##     gui.password_var.set("Abcde123")
##     assert gui.login()
##     SubjectController(gui.database).enrol_subject(student)
##     assert gui.refresh_subjects()
##     assert len(gui.subject_table.get_children()) == 1
## 
## 
## def test_gui_deleted_account_returns_to_login(gui, student):
##     """A GUI session whose account is removed cannot continue enrolling."""
##     gui.email_var.set(student.email)
##     gui.password_var.set("Abcde123")
##     assert gui.login()
##     gui.database.clear_students()
##     assert not gui.refresh_subjects()
##     assert gui.current_student is None
##     assert "not found" in gui.errors[-1]
