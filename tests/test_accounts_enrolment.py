"""Exercise account/enrolment rules and persistence across fresh controller instances."""

import pytest

from database import Database, DatabaseError
from grade import Grade
from student import Student
from student_controller import StudentController
from subject import Subject
from subject_controller import SubjectController
from validator import Validator


@pytest.mark.parametrize("email", ["", "test@example.com", "test@university.com.extra", "bad email@university.com"])
def test_invalid_emails(email):
    """Reject missing or non-university email formats."""
    assert not Validator.validate_email(email)


@pytest.mark.parametrize("password", ["", "abcde123", "Abcd123", "Abcde12", "Abcde123!", " Abcde123", "Abcde123 ", "Abcde１２３"])
def test_invalid_passwords(password):
    """Reject passwords outside the original five-letter/three-digit pattern."""
    assert not Validator.validate_password(password)


@pytest.mark.parametrize("password", ["Abcde123", "Abcdef1234", "ABCDE123"])
def test_valid_passwords(password):
    """Accept the documented minimum pattern and longer valid variants."""
    assert Validator.validate_password(password)


def test_registration_login_and_duplicates(database, student):
    """Persist identity, support case-insensitive email and reject duplicate accounts."""
    accounts = StudentController(Database(database.filename))
    assert len(student.student_id) == 6 and 1 <= int(student.student_id) <= 999999
    assert accounts.authenticate("TEST@university.com", "Abcde123").student_id == student.student_id
    with pytest.raises(ValueError, match="already exists"):
        accounts.register("Duplicate", "TEST@university.com", "Abcde123")
    with pytest.raises(ValueError, match="Invalid email or password"):
        accounts.authenticate(student.email, "Wrong123")
    with pytest.raises(ValueError, match="required"):
        accounts.authenticate("", "")


def test_blank_name_leaves_database_unchanged(database):
    """A rejected registration must not create a partial student record."""
    with pytest.raises(ValueError, match="Name is required"):
        StudentController(database).register("   ", "new@university.com", "Abcde123")
    assert database.read_students() == []


def test_student_id_collision_is_resolved(database, monkeypatch):
    """Resolve repeated random IDs and retain leading zeroes."""
    monkeypatch.setattr("student_controller.random.randint", lambda low, high: 1)
    accounts = StudentController(database)
    first = accounts.register("First", "first@university.com", "Abcde123")
    second = accounts.register("Second", "second@university.com", "Abcde123")
    assert (first.student_id, second.student_id) == ("000001", "000002")


@pytest.mark.parametrize("mark,grade", [(25, "Z"), (49, "Z"), (50, "P"), (64, "P"), (65, "C"), (74, "C"), (75, "D"), (84, "D"), (85, "HD"), (100, "HD")])
def test_grade_boundaries(mark, grade):
    """Check every lower/upper grade boundary specified on PDF page 13."""
    assert Subject(1, mark).grade == grade
    assert Grade.from_mark(mark) == grade


def test_subject_enrolment_limit_and_reopen(database, student):
    """Enforce the limit from storage even when a caller holds a stale student object."""
    service = SubjectController(database)
    stale = database.find_student_by_id(student.student_id)
    for _ in range(4):
        enrolled = service.enrol_subject(student)
        assert 1 <= enrolled.subject_id <= 999 and 25 <= enrolled.mark <= 100
    assert len({item.subject_id for item in student.subjects}) == 4
    with pytest.raises(ValueError, match="four"):
        service.enrol_subject(stale)
    reopened = Database(database.filename).find_student_by_id(student.student_id)
    assert len(reopened.subjects) == 4


def test_unique_subject_ids_across_students(database, student):
    """New enrolment records must have unused IDs across the shared database."""
    other = StudentController(database).register("Other", "other@university.com", "Abcde123")
    service = SubjectController(database)
    ids = [service.enrol_subject(owner).subject_id for owner in (student, other, student, other)]
    assert len(set(ids)) == 4


def test_remove_second_subject_then_enrol_again(database, student):
    """Regression: removing the second subject must leave the first subject untouched."""
    service = SubjectController(database)
    enrolled = [service.enrol_subject(student) for _ in range(4)]
    service.remove_subject(student, f"{enrolled[1].subject_id:03d}")
    ids = [subject.subject_id for subject in database.read_students()[0].subjects]
    assert ids == [enrolled[index].subject_id for index in (0, 2, 3)]
    service.enrol_subject(student)
    assert len(student.subjects) == 4


@pytest.mark.parametrize("subject_id", ["abc", "", "000", "1000", "-1", "1.5"])
def test_bad_subject_removal_is_non_destructive(database, student, subject_id):
    """Invalid selection must leave the stored subject list unchanged."""
    service = SubjectController(database)
    service.enrol_subject(student)
    snapshot = database.filename.read_bytes()
    with pytest.raises(ValueError):
        service.remove_subject(student, subject_id)
    assert database.filename.read_bytes() == snapshot


def test_unknown_subject_is_not_removed(database, student):
    """Reject an unowned subject without removing another enrolment."""
    service = SubjectController(database)
    subject = service.enrol_subject(student)
    unknown = 999 if subject.subject_id != 999 else 998
    with pytest.raises(ValueError, match="not found"):
        service.remove_subject(student, unknown)
    assert len(database.read_students()[0].subjects) == 1


def test_password_change_validation_and_persistence(database, student):
    """Reject bad replacements and persist a valid password across application restarts."""
    service = SubjectController(database)
    with pytest.raises(ValueError):
        service.change_password(student, "bad")
    assert database.read_students()[0].password == "Abcde123"
    service.change_password(student, "Newpass456")
    accounts = StudentController(Database(database.filename))
    assert accounts.authenticate(student.email, "Newpass456").student_id == student.student_id
    with pytest.raises(ValueError):
        accounts.authenticate(student.email, "Abcde123")


def test_model_rejects_duplicate_and_fifth_subject():
    """Keep the four-subject and duplicate-ID invariants inside the Student entity too."""
    student = Student("000001", "Model", "model@university.com", "Abcde123")
    for subject_id in range(1, 5):
        assert student.enrol_subject(Subject(subject_id, 50))
    assert not student.enrol_subject(Subject(5, 60))
    assert student.remove_subject("002")
    assert not student.enrol_subject(Subject(1, 50))
    assert [subject.subject_id for subject in student.subjects] == [1, 3, 4]


def test_failed_save_does_not_change_session(database, student, monkeypatch):
    """Keep the caller's session unchanged if persisting an enrolment fails."""
    def fail_write(students):
        """Simulate storage becoming unwritable during an operation."""
        raise DatabaseError("Simulated write failure")

    monkeypatch.setattr(database, "write_students", fail_write)
    with pytest.raises(DatabaseError):
        SubjectController(database).enrol_subject(student)
    assert student.subjects == []
    assert database.read_students()[0].subjects == []
