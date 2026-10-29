"""An individual enrolled subject and its randomly generated result."""

import random

from grade import Grade


class Subject:
    """Store a three-digit subject identifier, mark and calculated grade."""

    def __init__(self, subject_id=None, mark=None):
        """Create a random subject, or accept explicit values for loading and tests."""
        self.subject_id = random.randint(1, 999) if subject_id is None else int(subject_id)
        self.mark = random.randint(25, 100) if mark is None else mark
        if not 1 <= self.subject_id <= 999:
            raise ValueError("Subject ID must be between 001 and 999.")
        if type(self.mark) is not int or not 25 <= self.mark <= 100:
            raise ValueError("Subject mark must be an integer between 25 and 100.")
        self.grade = self.calculate_grade()

    def calculate_grade(self):
        """Calculate this subject's grade from its mark."""
        return Grade.from_mark(self.mark)

    def __str__(self):
        """Format the ID with leading zeroes and include the mark and grade."""
        return f"Subject::{self.subject_id:03d} -- mark = {self.mark} -- grade = {self.grade}"


## ORIGINAL CODE - retained as requested; active implementation appears above.
## import random
## class Subject:
##     def __init__(self):
##         self.subject_id = random.randint(1,999)
##         self.mark = random.randint(25,100)
##         self.grade = self.calculate_grade()
## 
##     def calculate_grade(self):
##         if self.mark >= 85:
##             return "HD"
##         elif self.mark >= 75:
##             return "D"
##         elif self.mark >= 65:
##             return "C"
##         elif self.mark >= 50:
##             return "P"
##         else:
##             return "Z"
## 
##     def __str__(self):
##         return f"Subject::{self.subject_id:03d} -- mark = {self.mark} -- grade = {self.grade}"
