"""Isolated integration fixtures for Member 4; production students.data is not used."""

import pytest

from database import Database
from student_controller import StudentController


@pytest.fixture
def database(tmp_path, monkeypatch):
    """Redirect every legacy Database() constructor to a private test file."""
    monkeypatch.setattr(Database, "_default_filename", tmp_path / "students.data")
    return Database()


@pytest.fixture
def student(database, monkeypatch):
    """Register a real student through Member 1's original interactive implementation."""
    responses = iter(("Test Student", "test@university.com", "Abcde123"))
    with monkeypatch.context() as patch:
        patch.setattr("builtins.input", lambda prompt: next(responses))
        StudentController().register_student()
    return database.find_student_by_email("test@university.com")
