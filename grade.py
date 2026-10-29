"""Grade categories and shared mark boundaries from the analysis document."""

from enum import Enum


class Grade(str, Enum):
    """Represent the five subject outcomes while retaining string compatibility."""

    Z = "Z"
    P = "P"
    C = "C"
    D = "D"
    HD = "HD"

    def __str__(self):
        """Display the grade label in CLI and Tkinter widgets."""
        return self.value

    @classmethod
    def from_mark(cls, mark):
        """Map a mark to Z/P/C/D/HD using the PDF's 50/65/75/85 boundaries."""
        if not 0 <= mark <= 100:
            raise ValueError("Mark must be between 0 and 100.")
        for minimum, grade in ((85, cls.HD), (75, cls.D), (65, cls.C), (50, cls.P)):
            if mark >= minimum:
                return grade
        return cls.Z
