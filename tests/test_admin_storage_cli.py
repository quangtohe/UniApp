"""Verify official average-based reporting, sample CLI flows and safe file storage."""

import pickle
import subprocess
import sys
from pathlib import Path

import pytest

from admin_controller import AdminController
from database import Database, DatabaseError
from student import Student
from student_controller import StudentController
from subject import Subject
from subject_controller import SubjectController


def test_admin_groups_students_by_average(database, student):
    """Four mixed-grade subjects yield one P student with average 55, never four rows."""
    student.subjects = [Subject(i + 1, mark) for i, mark in enumerate((25, 85, 50, 60))]
    database.write_students([student])
    admin = AdminController(database)
    grades = admin.results_by_grade()
    assert [item.student_id for item in grades["P"]] == [student.student_id]
    assert sum(len(group) for group in grades.values()) == 1
    assert student.average_mark() == 55
    assert len(admin.pass_fail_results()["PASS"]) == 1
    assert admin.pass_fail_results()["FAIL"] == []


@pytest.mark.parametrize("marks,grade,outcome", [((49, 49, 50, 50), "Z", "FAIL"), ((49, 49, 51, 51), "P", "PASS"), ((64, 65, 65, 65), "P", "PASS"), ((65, 65, 65, 65), "C", "PASS"), ((75, 75, 75, 75), "D", "PASS"), ((85, 85, 85, 85), "HD", "PASS")])
def test_average_boundaries_are_not_rounded_before_classification(database, student, marks, grade, outcome):
    """Classify actual average values at the official pass and grade boundaries."""
    student.subjects = [Subject(i + 1, mark) for i, mark in enumerate(marks)]
    database.write_students([student])
    admin = AdminController(database)
    assert admin.results_by_grade()[grade][0].student_id == student.student_id
    assert admin.pass_fail_results()[outcome][0].student_id == student.student_id


def test_average_recalculates_after_enrol_remove_and_reopen(database, student, monkeypatch):
    """Current averages follow the enrolment list and remain correct after reopening."""
    student.subjects = [Subject(1, 25)]
    database.write_students([student])
    monkeypatch.setattr("subject.random.randint", lambda low, high: 100)
    service = SubjectController(database)
    enrolled = service.enrol_subject(student)
    assert student.average_mark() == 62.5
    assert Database(database.filename).read_students()[0].average_mark() == 62.5
    service.remove_subject(student, enrolled.subject_id)
    assert student.average_mark() == 25
    service.remove_subject(student, 1)
    assert student.average_mark() is None and student.overall_grade() is None


def test_unenrolled_students_are_not_failures(database, student, capsys):
    """Leave accounts with no marks outside PASS/FAIL and explicitly show NOT GRADED."""
    admin = AdminController(database)
    assert admin.pass_fail_results() == {"FAIL": [], "PASS": []}
    admin.partition_pass_fail()
    output = capsys.readouterr().out
    assert "FAIL --> []" in output and "PASS --> []" in output
    assert "NOT GRADED" in output


def test_admin_listing_and_average_output(database, student, capsys):
    """Match identity/average report formats without printing credentials."""
    student.subjects = [Subject(i + 1, mark) for i, mark in enumerate((60, 65, 70, 78))]
    database.write_students([student])
    admin = AdminController(database)
    admin.show_all_students()
    admin.group_students_by_grade()
    output = capsys.readouterr().out
    assert f"{student.name} :: {student.student_id} --> Email: {student.email}" in output
    assert "GRADE: C - MARK: 68.25" in output
    assert student.password not in output


def test_admin_remove_and_deleted_session(database, student):
    """Deleting one student removes their enrolments and invalidates old GUI sessions."""
    service = SubjectController(database)
    service.enrol_subject(student)
    admin = AdminController(database)
    assert not admin.remove_student_by_id("000000")
    assert admin.remove_student_by_id(student.student_id)
    assert Database(database.filename).read_students() == []
    with pytest.raises(ValueError, match="not found"):
        service.enrol_subject(student)


def test_admin_unknown_id_and_cancel_clear_preserve_data(database, student, monkeypatch):
    """A missing ID and an N clear confirmation must leave all stored data intact."""
    admin = AdminController(database)
    responses = iter(["000000", "N"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(responses))
    admin.remove_student()
    admin.clear_all_students()
    assert len(database.read_students()) == 1


def test_admin_sample_remove_and_confirm_clear(database, student, monkeypatch):
    """Exercise removal by ID and Y-confirmed clear exactly as in the sample flow."""
    admin = AdminController(database)
    monkeypatch.setattr("builtins.input", lambda prompt: student.student_id)
    admin.remove_student()
    assert database.read_students() == []
    StudentController(database).register("Again", "again@university.com", "Abcde123")
    monkeypatch.setattr("builtins.input", lambda prompt: "Y")
    admin.clear_all_students()
    assert Database(database.filename).read_students() == []


@pytest.mark.parametrize("content", [b"", b"not a pickle", pickle.dumps({"bad": "shape"})])
def test_corrupt_database_preserved(tmp_path, content):
    """Report empty/corrupt files without replacing them with a new empty database."""
    path = tmp_path / "students.data"
    path.write_bytes(content)
    with pytest.raises(DatabaseError):
        Database(path).read_students()
    assert path.read_bytes() == content


def test_legacy_pickle_compatibility(tmp_path):
    """Read the original Student/Subject layout with a string grade without migration."""
    legacy = Student("000001", "Legacy", "legacy@university.com", "Abcde123")
    subject = Subject(4, 75)
    subject.grade = "D"
    legacy.subjects = [subject]
    path = tmp_path / "students.data"
    path.write_bytes(pickle.dumps([legacy], protocol=4))
    loaded = Database(path).read_students()[0]
    assert loaded.subjects[0].grade == "D" and loaded.average_mark() == 75


def test_unexpected_pickle_class_rejected(tmp_path):
    """Reject unexpected executable/model types in a database file."""
    path = tmp_path / "students.data"
    path.write_bytes(pickle.dumps(Path("unexpected")))
    with pytest.raises(DatabaseError, match="Unexpected object"):
        Database(path).read_students()


def test_atomic_replace_failure_keeps_original(database, student, monkeypatch):
    """A failed atomic replacement must preserve the original data and clean its temp file."""
    snapshot = database.filename.read_bytes()

    def fail_replace(source, target):
        """Simulate a locked target at the last step of saving."""
        raise OSError("Simulated locked file")

    monkeypatch.setattr("database.os.replace", fail_replace)
    with pytest.raises(DatabaseError):
        database.write_students([])
    assert database.filename.read_bytes() == snapshot
    assert list(database.filename.parent.iterdir()) == [database.filename]


def test_password_confirmation_and_reuse(database, student):
    """Reject mismatched confirmation without saving and allow reusing a valid password."""
    service = SubjectController(database)
    snapshot = database.filename.read_bytes()
    with pytest.raises(ValueError, match="does not match"):
        service.change_password(student, "Newpass456", "Newpass457")
    assert database.filename.read_bytes() == snapshot
    assert service.change_password(student, "Abcde123", "Abcde123")


def test_end_to_end_cli_sample_menus_and_retries(tmp_path):
    """Follow real stdin through format retries, sign-up, enrolment, c-confirmation and admin."""
    path = tmp_path / "cli.data"
    commands = "\n".join(["S", "r", "bad", "bad", "cli@university.com", "Abcde123", "CLI Student", "l", "cli@university.com", "Abcde123", "s", "e", "c", "bad", "Newpass456", "Wrong123", "Newpass456", "x", "x", "A", "s", "g", "p", "x", "X", ""])
    result = subprocess.run([sys.executable, "main.py", "--data", str(path)], input=commands, text=True, capture_output=True, cwd=Path(__file__).resolve().parents[1], timeout=15)
    assert result.returncode == 0, result.stderr
    for expected in ("University System: (A)dmin, (S)tudent, or X :", "Student System (l/r/x):", "Student Course Menu (c/e/r/s/x):", "Admin System (c/g/p/r/s/x):", "Incorrect email or password format", "Enrolling Student CLI Student", "Showing 0 subjects", "Enrolling in Subject-", "You are now enrolled in 1 out of 4 subjects", "Updating Password", "Password does not match - try again", "Grade Grouping", "PASS/FAIL Partition", "Thank You"):
        assert expected in result.stdout
    student = Database(path).read_students()[0]
    assert student.password == "Newpass456" and len(student.subjects) == 1


def test_cli_duplicate_signup_does_not_prompt_for_name(database, student, monkeypatch, capsys):
    """An existing email must be rejected before requesting the Name field."""
    responses = iter([student.email, "Abcde123"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(responses))
    assert StudentController(database).register_student() is None
    assert "already exists" in capsys.readouterr().out
    assert len(database.read_students()) == 1


## PRE-CANVAS IMPLEMENTATION - retained as ## comments before course-aligned changes.
## """Verify result grouping, deletion, legacy storage and full University Menu flows."""
## 
## import pickle
## import subprocess
## import sys
## from pathlib import Path
## 
## import pytest
## 
## from admin_controller import AdminController
## from database import Database, DatabaseError
## from student import Student
## from student_controller import StudentController
## from subject import Subject
## from subject_controller import SubjectController
## 
## 
## def test_admin_groups_each_subject_not_the_average(database, student):
##     """A student with 25 and 85 must appear in both FAIL/Z and PASS/HD results."""
##     student.subjects = [Subject(1, 25), Subject(2, 85), Subject(3, 50)]
##     database.write_students([student])
##     admin = AdminController(database)
##     grades = admin.results_by_grade()
##     assert [subject.subject_id for owner, subject in grades["Z"]] == [1]
##     assert [subject.subject_id for owner, subject in grades["HD"]] == [2]
##     assert [subject.subject_id for owner, subject in grades["P"]] == [3]
##     outcomes = admin.pass_fail_results()
##     assert len(outcomes["PASS"]) == 2 and len(outcomes["FAIL"]) == 1
## 
## 
## def test_unenrolled_students_are_not_failures(database, student, capsys):
##     """Keep students with no marks out of FAIL and list them as not graded."""
##     admin = AdminController(database)
##     assert admin.pass_fail_results() == {"PASS": [], "FAIL": []}
##     admin.partition_pass_fail()
##     assert "Not graded (1 students)" in capsys.readouterr().out
## 
## 
## def test_admin_show_includes_subject_details(database, student, capsys):
##     """The all-students view must include owned subject IDs and marks."""
##     student.subjects = [Subject(7, 85)]
##     database.write_students([student])
##     AdminController(database).show_all_students()
##     output = capsys.readouterr().out
##     assert "Subject::007" in output and "mark = 85" in output
##     assert student.password not in output
## 
## 
## def test_admin_remove_and_deleted_session(database, student):
##     """Deleting a student also deletes enrolments and invalidates old session objects."""
##     service = SubjectController(database)
##     service.enrol_subject(student)
##     admin = AdminController(database)
##     assert not admin.remove_student_by_id("000000")
##     assert admin.remove_student_by_id(student.student_id)
##     assert Database(database.filename).read_students() == []
##     with pytest.raises(ValueError, match="not found"):
##         service.enrol_subject(student)
## 
## 
## def test_admin_cancel_remove_and_clear(database, student, monkeypatch):
##     """Declining either deletion prompt must preserve the original account."""
##     admin = AdminController(database)
##     responses = iter([student.student_id, "n", "no"])
##     monkeypatch.setattr("builtins.input", lambda prompt: next(responses))
##     admin.remove_student()
##     admin.clear_all_students()
##     assert len(database.read_students()) == 1
## 
## 
## def test_admin_confirmed_remove_and_clear(database, student, monkeypatch):
##     """Exercise the actual confirmation prompts and persist both deletion paths."""
##     admin = AdminController(database)
##     responses = iter([student.student_id, "y"])
##     monkeypatch.setattr("builtins.input", lambda prompt: next(responses))
##     admin.remove_student()
##     assert database.read_students() == []
##     StudentController(database).register("Again", "again@university.com", "Abcde123")
##     monkeypatch.setattr("builtins.input", lambda prompt: "CLEAR")
##     admin.clear_all_students()
##     assert Database(database.filename).read_students() == []
## 
## 
## @pytest.mark.parametrize("content", [b"", b"not a pickle", pickle.dumps({"bad": "shape"})])
## def test_corrupt_database_preserved(tmp_path, content):
##     """Report empty/corrupt data rather than silently resetting it."""
##     path = tmp_path / "students.data"
##     path.write_bytes(content)
##     database = Database(path)
##     with pytest.raises(DatabaseError):
##         database.read_students()
##     assert path.read_bytes() == content
## 
## 
## def test_legacy_pickle_compatibility(tmp_path):
##     """Load the old Student/Subject shape with a plain string grade without migration."""
##     legacy = Student("000001", "Legacy", "legacy@university.com", "Abcde123")
##     subject = Subject(4, 75)
##     subject.grade = "D"
##     legacy.subjects = [subject]
##     path = tmp_path / "students.data"
##     path.write_bytes(pickle.dumps([legacy], protocol=4))
##     assert Database(path).read_students()[0].subjects[0].grade == "D"
## 
## 
## def test_unexpected_pickle_class_rejected(tmp_path):
##     """Reject objects outside the application models when loading a data file."""
##     path = tmp_path / "students.data"
##     path.write_bytes(pickle.dumps(Path("unexpected")))
##     with pytest.raises(DatabaseError, match="Unexpected object"):
##         Database(path).read_students()
## 
## 
## def test_atomic_replace_failure_keeps_original(database, student, monkeypatch):
##     """A failed final replace must preserve the file and remove its temporary snapshot."""
##     snapshot = database.filename.read_bytes()
## 
##     def fail_replace(source, target):
##         """Simulate an operating-system error at the last step of a save."""
##         raise OSError("Simulated locked file")
## 
##     monkeypatch.setattr("database.os.replace", fail_replace)
##     with pytest.raises(DatabaseError):
##         database.write_students([])
##     assert database.filename.read_bytes() == snapshot
##     assert list(database.filename.parent.iterdir()) == [database.filename]
## 
## 
## def test_end_to_end_cli_university_menu(tmp_path):
##     """Register/login/enrol, change password, visit admin and exit through real stdin."""
##     path = tmp_path / "cli.data"
##     commands = "\n".join(["s", "r", "CLI Student", "cli@university.com", "Abcde123", "l", "cli@university.com", "Abcde123", "e", "s", "p", "Newpass456", "x", "x", "a", "s", "g", "p", "x", "x", ""])
##     result = subprocess.run([sys.executable, "main.py", "--data", str(path)], input=commands, text=True, capture_output=True, cwd=Path(__file__).resolve().parents[1], timeout=15)
##     assert result.returncode == 0, result.stderr
##     assert "Registration successful" in result.stdout
##     assert "Subject enrolled successfully" in result.stdout
##     assert "Password updated successfully" in result.stdout
##     assert "Total students: 1" in result.stdout
##     student = Database(path).read_students()[0]
##     assert student.password == "Newpass456" and len(student.subjects) == 1
