"""Regression tests for removing exactly the selected subject through the model and CLI."""

import pytest

from student import Student
from subject import Subject
from subject_controller import SubjectController
from database import DatabaseError
from gui_controller import GUIController


@pytest.fixture
def enrolled_student(database, student):
    """Persist three distinct subjects so removing a later row can expose the old bug."""
    for subject_id, mark in ((101, 60), (202, 70), (303, 80)):
        subject = Subject()
        subject.subject_id = subject_id
        subject.mark = mark
        subject.grade = subject.calculate_grade()
        student.enrol_subject(subject)
    database.write_students([student])
    return student


@pytest.mark.parametrize("index", (0, 1, 2))
def test_model_removes_only_the_selected_subject(enrolled_student, index):
    """Removing any row must preserve the identity, marks and order of the other rows."""
    original = list(enrolled_student.subjects)
    assert enrolled_student.remove_subject(original[index])
    assert enrolled_student.subjects == original[:index] + original[index + 1:]


def test_unknown_subject_leaves_enrolments_unchanged(enrolled_student):
    """A subject that is not enrolled must return False and leave every row intact."""
    original = list(enrolled_student.subjects)
    missing = Subject()
    missing.subject_id = 404
    assert not enrolled_student.remove_subject(missing)
    assert enrolled_student.subjects == original


def test_removing_from_empty_enrolments_returns_false(student):
    """An account without enrolled subjects has nothing to remove."""
    assert not student.remove_subject(Subject())
    assert student.subjects == []


def test_cli_removal_persists_the_selected_subject_only(database, enrolled_student, monkeypatch, capsys):
    """The real CLI controller must remove the middle subject and preserve other accounts."""
    ## other = Student("999999", "Other Student", "other@university.com", "Abcde123")
    other_id = "999998" if enrolled_student.student_id == "999999" else "999999"
    other = Student(other_id, "Other Student", "other@university.com", "Abcde123")
    database.write_students([enrolled_student, other])
    before = [(subject.subject_id, subject.mark, subject.grade) for subject in enrolled_student.subjects]
    monkeypatch.setattr("builtins.input", lambda prompt: "202")
    SubjectController().remove_subject(enrolled_student)
    assert "Subject removed successfully." in capsys.readouterr().out
    saved = database.find_student_by_id(enrolled_student.student_id)
    assert [(subject.subject_id, subject.mark, subject.grade) for subject in saved.subjects] == [before[0], before[2]]
    assert database.find_student_by_id(other.student_id).email == other.email
    assert len(database.read_students()) == 2


@pytest.mark.parametrize("selection,message", (("404", "Subject ID not found."), ("invalid", "valid numeric subject ID")))
def test_cli_invalid_selection_does_not_save(database, enrolled_student, monkeypatch, capsys, selection, message):
    """Invalid and unknown IDs must not alter the persisted enrolments."""
    original = database.filename.read_bytes()
    monkeypatch.setattr("builtins.input", lambda prompt: selection)
    SubjectController().remove_subject(enrolled_student)
    assert message in capsys.readouterr().out
    assert database.filename.read_bytes() == original


def test_gui_service_removes_fresh_enrolment_and_preserves_other_students(database, enrolled_student):
    """An old GUI copy must remove only its own selected subject using persisted records."""
    other_id = "999998" if enrolled_student.student_id == "999999" else "999999"
    other = Student(other_id, "Other Student", "other@university.com", "Abcde123")
    other.subjects = [enrolled_student.subjects[1]]
    database.write_students([enrolled_student, other])
    enrolled_student.subjects = []
    removed = GUIController(database).remove_subject(enrolled_student, 202)
    assert removed.subject_id == 202
    assert [subject.subject_id for subject in enrolled_student.subjects] == [101, 303]
    assert [subject.subject_id for subject in database.find_student_by_id(other_id).subjects] == [202]
    assert len(database.read_students()) == 2


def test_gui_service_rejects_unknown_or_already_removed_subject(database, enrolled_student):
    """Unknown and repeated removals must leave the file and current session unchanged."""
    service = GUIController(database)
    for subject_id in (404, 202):
        if subject_id == 202:
            service.remove_subject(enrolled_student, 202)
        original = database.filename.read_bytes()
        session = list(enrolled_student.subjects)
        with pytest.raises(ValueError, match="no longer enrolled"):
            service.remove_subject(enrolled_student, subject_id)
        assert database.filename.read_bytes() == original and enrolled_student.subjects == session


def test_gui_service_rejects_removed_student(database, enrolled_student):
    """A stale account must not recreate itself when requesting an enrolment removal."""
    database.clear_students()
    with pytest.raises(ValueError, match="not found"):
        GUIController(database).remove_subject(enrolled_student, 202)
    assert database.read_students() == []


def test_gui_service_save_failure_preserves_session_and_file(database, enrolled_student, monkeypatch):
    """A failed write must not remove a row from the GUI's in-memory Student."""
    original = database.filename.read_bytes()
    session = list(enrolled_student.subjects)

    def fail_write(students):
        """Simulate a storage error before committing the updated Student."""
        raise DatabaseError("Subject removal write failed")

    monkeypatch.setattr(database, "write_students", fail_write)
    with pytest.raises(DatabaseError, match="write failed"):
        GUIController(database).remove_subject(enrolled_student, 202)
    assert database.filename.read_bytes() == original and enrolled_student.subjects == session


def test_gui_service_detects_a_removal_that_was_not_persisted(database, enrolled_student, monkeypatch):
    """Do not report success when the legacy save returns without changing the file."""
    service = GUIController(database)
    monkeypatch.setattr(service.subject_controller, "save_student", lambda student: None)
    with pytest.raises(ValueError, match="could not be saved"):
        service.remove_subject(enrolled_student, 202)
    assert len(enrolled_student.subjects) == 3
    assert len(database.find_student_by_id(enrolled_student.student_id).subjects) == 3


def test_gui_service_removing_last_subject_resets_summary_and_frees_a_place(database, enrolled_student):
    """Removing all enrolments must restore the ungraded state and permit enrolment again."""
    service = GUIController(database)
    for subject_id in (101, 202, 303):
        service.remove_subject(enrolled_student, subject_id)
    assert service.summary(enrolled_student) == {"count": 0, "average": None, "grade": None}
    service.enrol_subject(enrolled_student)
    assert len(database.find_student_by_id(enrolled_student.student_id).subjects) == 1
