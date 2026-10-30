"""Real hidden-widget tests of the four Member 4 Tkinter windows."""

import tkinter as tk

import pytest

from gui_uni_app import GUIUniApp, EnrolmentWindow, SubjectWindow, ExceptionWindow
from subject_controller import SubjectController


@pytest.fixture(scope="module")
def tk_root():
    """Use one Tk interpreter, matching the application's normal root lifecycle."""
    try:
        root = tk.Tk()
    except tk.TclError as error:
        if "no display name" in str(error) or "couldn't connect to display" in str(error):
            pytest.skip(f"Display unavailable: {error}")
        raise
    root.withdraw()
    yield root
    root.destroy()


@pytest.fixture
def gui(database, tk_root):
    """Create fresh views and test data without opening desktop windows."""
    application = GUIUniApp(root=tk_root, database=database, visible=False)
    yield application
    application.show_login_window()
    application.login_view.destroy()
    tk_root.unbind("<Return>")


def sign_in(gui, student):
    """Activate the actual sign-in callback with a Member 1 registered account."""
    gui.email_var.set(student.email)
    gui.password_var.set(student.password)
    gui.login_button.invoke()
    assert gui.current_student.student_id == student.student_id


def test_login_errors_use_exception_window(gui, student):
    """Empty, malformed and unmatched credentials must be shown in the fourth window."""
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


def test_four_windows_and_fifth_enrolment_exception(gui, student, database):
    """Use real buttons to enrol four subjects and verify the rejected fifth attempt."""
    sign_in(gui, student)
    assert isinstance(gui.enrolment_window, EnrolmentWindow)
    gui.enrolment_window.subjects_button.invoke()
    assert isinstance(gui.subject_window, SubjectWindow)
    assert "No subjects" in gui.subject_window.status_var.get()
    for _ in range(4):
        gui.enrol_button.invoke()
    assert len(gui.subject_table.get_children()) == 4
    assert "4/4" in gui.count_var.get()
    gui.enrol_button.invoke()
    assert isinstance(gui.exception_window, ExceptionWindow)
    assert "four" in gui.exception_window.message_var.get()
    windows = (gui.root, gui.enrolment_window, gui.subject_window, gui.exception_window)
    assert len({str(window) for window in windows}) == 4
    assert len(database.read_students()[0].subjects) == 4


def test_logout_and_relogin_preserve_file_records(gui, student):
    """Logout must close children, clear fields and retain persisted enrolments."""
    sign_in(gui, student)
    gui.enrol_button.invoke()
    gui.show_subject_window()
    gui.enrolment_window.logout_button.invoke()
    assert gui.current_student is None and gui.subject_window is None
    assert gui.email_var.get() == "" and gui.password_var.get() == ""
    sign_in(gui, student)
    assert gui.show_subject_window()
    assert len(gui.subject_table.get_children()) == 1


def test_gui_refresh_reads_subjects_created_by_legacy_cli(gui, student):
    """Changes made with Member 2's original controller must appear after GUI refresh."""
    sign_in(gui, student)
    gui.show_subject_window()
    SubjectController().enrol_subject(student)
    assert gui.refresh_subjects()
    assert len(gui.subject_table.get_children()) == 1


def test_deleted_account_returns_to_login(gui, student):
    """A deleted account must not continue enrolment from an old GUI session."""
    sign_in(gui, student)
    gui.database.clear_students()
    assert not gui.refresh_subjects()
    assert gui.current_student is None and gui.enrolment_window is None
    assert "not found" in gui.exception_window.message_var.get()


@pytest.fixture
def admin_gui(gui):
    """Reuse the single Tk interpreter with explicitly enabled demo admin access."""
    from admin_gui_controller import AdminGUIController

    gui.demo_mode = True
    gui.admin_service = AdminGUIController(gui.database, demo_mode=True)
    gui.set_login_role("admin")
    assert gui.login()
    return gui


def test_admin_role_rejects_student_credentials_and_student_role_rejects_admin(gui, student):
    """Selecting a role must authenticate with that role's independent account store."""
    from admin_gui_controller import AdminGUIController
    from demo_data import DEMO_ADMIN_EMAIL, DEMO_ADMIN_PASSWORD

    gui.admin_service = AdminGUIController(gui.database, demo_mode=True)
    gui.set_login_role("admin")
    gui.email_var.set(student.email)
    gui.password_var.set(student.password)
    assert not gui.login() and gui.admin_window is None
    gui.set_login_role("student")
    gui.email_var.set(DEMO_ADMIN_EMAIL)
    gui.password_var.set(DEMO_ADMIN_PASSWORD)
    assert not gui.login() and gui.current_student is None
    assert not gui.show_admin_window()


def test_admin_dashboard_groups_searches_and_refreshes(admin_gui, student):
    """Render persisted records with ungraded grouping and live search."""
    window = admin_gui.admin_window
    assert admin_gui.current_admin is not None and admin_gui.current_student is None
    window.refresh_button.invoke()
    assert window.tree.get_children() == (f"student:{student.student_id}",)
    assert window.metric_vars["students"].get() == "1"
    for view in ("Group by grade", "PASS / FAIL"):
        window.view_var.set(view)
        window.refresh_students()
        assert window.tree.get_children() == ("group:NOT GRADED",)
        window.tree.selection_set("group:NOT GRADED")
        window._selection_changed()
        assert window.remove_button.instate(["disabled"])
    window.search_var.set("no matching account")
    window.refresh_students()
    assert not window.tree.get_children()
    assert window.empty_label.cget("text") == "No matching students"
    assert window.metric_vars["students"].get() == "1"


def test_admin_remove_can_cancel_then_removes_only_selection(admin_gui, student, database):
    """Exercise actual selection and dialog buttons against a disposable database."""
    from student import Student

    records = database.read_students()
    records.append(Student("999999", "Keep Student", "keep@university.com", "Abcde123"))
    database.write_students(records)
    window = admin_gui.admin_window
    window.refresh_students()
    window.tree.selection_set(f"student:{student.student_id}")
    window._selection_changed()
    window.remove_button.invoke()
    admin_gui.confirmation_window.cancel_button.invoke()
    assert len(database.read_students()) == 2
    window.remove_button.invoke()
    admin_gui.confirmation_window.confirm_button.invoke()
    assert [s.student_id for s in database.read_students()] == ["999999"]
    assert admin_gui.confirmation_window is None
    assert "successfully" in window.status_var.get()


def test_admin_clear_requires_typed_phrase_and_logout_revokes_access(admin_gui, student, database):
    """Typing CLEAR enables confirmation, clears storage and logout revokes the session."""
    window = admin_gui.admin_window
    window.refresh_students()
    window.clear_button.invoke()
    dialog = admin_gui.confirmation_window
    assert dialog.confirm_button.instate(["disabled"])
    dialog.phrase_var.set("clear")
    assert not dialog.confirm()
    assert len(database.read_students()) == 1
    dialog.phrase_var.set("CLEAR")
    dialog.confirm_button.invoke()
    assert database.read_students() == []
    assert window.metric_vars["students"].get() == "0"
    window.logout_button.invoke()
    assert admin_gui.current_admin is None and admin_gui.admin_window is None
    assert admin_gui.password_var.get() == "" and admin_gui.email_var.get() == ""
    with pytest.raises(PermissionError):
        admin_gui.admin_service.report()


def fill_registration(window, email="new@university.com", confirmation="Abcde123"):
    """Fill the actual registration fields with a reusable new Student example."""
    window.name_var.set("New Student")
    window.email_var.set(email)
    window.password_var.set("Abcde123")
    window.confirmation_var.set(confirmation)


def test_register_button_creates_account_and_returns_to_login(gui, database):
    """Exercise the real buttons, success message, masked fields and subsequent login."""
    gui.login_view.register_button.invoke()
    window = gui.registration_window
    assert window is not None and gui.current_student is None
    fill_registration(window)
    for key in ("password", "confirmation"):
        assert window.entries[key].cget("show") == "*"
    window.show_password_var.set(True)
    window.toggle_password()
    assert window.entries["confirmation"].cget("show") == ""
    assert not gui.login()
    window.register_button.invoke()
    assert gui.registration_window is None and gui.current_student is None
    assert gui.email_var.get() == "new@university.com" and gui.password_var.get() == ""
    assert window.password_var.get() == "" and window.confirmation_var.get() == ""
    account = database.read_students()[0]
    assert account.student_id in gui.login_view.notice_var.get()
    gui.password_var.set("Abcde123")
    gui.login_button.invoke()
    assert gui.current_student.student_id == account.student_id


def test_registration_error_keeps_form_and_allows_retry(gui, database):
    """Invalid input must show an error owned by the form and allow correction."""
    gui.show_registration_window()
    window = gui.registration_window
    fill_registration(window, confirmation="Wrong123")
    assert not gui.register_student()
    assert "do not match" in gui.exception_window.message_var.get()
    assert gui.exception_window.master is window
    assert database.read_students() == []
    gui.exception_window.ok_button.invoke()
    assert gui.registration_window is window and window.name_var.get() == "New Student"
    window.confirmation_var.set("Abcde123")
    assert gui.register_student()
    assert gui.exception_window is None and len(database.read_students()) == 1


def test_registration_duplicate_and_storage_error_stay_on_form(gui, student, monkeypatch):
    """Neither duplicate credentials nor storage failure may show success or start a session."""
    from database import DatabaseError

    gui.show_registration_window()
    window = gui.registration_window
    fill_registration(window, email=student.email)
    assert not gui.register_student()
    assert "already exists" in gui.exception_window.message_var.get()
    gui.exception_window.ok_button.invoke()
    window.email_var.set("new@university.com")

    def fail_save(students):
        """Simulate a database failure during the registration callback."""
        raise DatabaseError("Cannot save registration")

    monkeypatch.setattr(gui.database, "write_students", fail_save)
    assert not gui.register_student()
    assert "Cannot save" in gui.exception_window.message_var.get()
    assert gui.registration_window is window and gui.current_student is None
    assert gui.login_view.notice_var.get() == ""


def test_cancel_registration_discards_fields_without_saving(gui, database):
    """Cancel or window close must discard secrets and permit opening a fresh form."""
    gui.show_registration_window()
    window = gui.registration_window
    fill_registration(window)
    window.cancel_button.invoke()
    assert gui.registration_window is None and database.read_students() == []
    assert window.password_var.get() == ""
    gui.show_registration_window()
    assert gui.registration_window.password_var.get() == ""
    assert gui.registration_window.name_var.get() == ""


def test_registration_is_available_only_for_signed_out_students(gui, student):
    """The Admin role and active sessions cannot create accounts through this form."""
    gui.set_login_role("admin")
    assert not gui.login_view.register_button.winfo_manager()
    assert not gui.show_registration_window()
    assert not gui.register_student()
    gui.set_login_role("student")
    assert gui.login_view.register_button.winfo_manager() == "grid"
    sign_in(gui, student)
    assert not gui.show_registration_window()
    assert not gui.register_student()
