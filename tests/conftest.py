"""Isolated fixtures: no test opens or rewrites the project's students.data."""

import pytest

from database import Database
from student_controller import StudentController


@pytest.fixture
def database(tmp_path):
    """Provide an empty database private to each test."""
    return Database(tmp_path / "students.data")


@pytest.fixture
def student(database):
    """Register one valid account through the actual persistence service."""
    return StudentController(database).register("Test Student", "test@university.com", "Abcde123")
