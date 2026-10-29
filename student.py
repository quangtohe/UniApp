"""Student identity, enrolment and aggregate results used by both interfaces."""

from grade import Grade
from validator import Validator


class Student:
    """Own student data and the rules that operate on the student's subjects."""

    MAX_SUBJECTS = 4

    def __init__(self, student_id, name, email, password):
        """Initialise identity and an empty list, keeping the legacy pickle field names."""
        self.student_id = str(student_id).zfill(6)
        self.name = name
        self.email = email
        self.password = password
        self.subjects = []

    def change_password(self, new_password):
        """Replace a valid password; reusing the existing password is permitted."""
        if not Validator.validate_password(new_password):
            raise ValueError(Validator.PASSWORD_HELP)
        self.password = new_password

    def can_enrol(self):
        """Return whether there is room within the four-subject maximum."""
        return len(self.subjects) < self.MAX_SUBJECTS

    def enrol_subject(self, subject):
        """Add a nonduplicate subject when space is available."""
        if not self.can_enrol() or any(item.subject_id == subject.subject_id for item in self.subjects):
            return False
        self.subjects.append(subject)
        return True

    def remove_subject(self, subject):
        """Remove the selected subject object or ID without affecting other enrolments."""
        try:
            subject_id = int(getattr(subject, "subject_id", subject))
        except (ValueError, TypeError):
            return False
        for index, enrolled in enumerate(self.subjects):
            if enrolled.subject_id == subject_id:
                del self.subjects[index]
                return True
        return False

    def get_subjects(self):
        """Return a separate list so views cannot add/remove owned subjects directly."""
        return list(self.subjects)

    def average_mark(self):
        """Recalculate the current mean on demand; no subjects means not graded yet."""
        if not self.subjects:
            return None
        return sum(subject.mark for subject in self.subjects) / len(self.subjects)

    def overall_grade(self):
        """Calculate the student's grade from the unrounded current average."""
        average = self.average_mark()
        return None if average is None else Grade.from_mark(average)

    def result_summary(self):
        """Format one student and their average result for admin grouping/partitioning."""
        average = self.average_mark()
        result = "NOT GRADED" if average is None else f"GRADE: {self.overall_grade()} - MARK: {average:.2f}"
        return f"{self.name} :: {self.student_id} --> {result}"

    def show_subjects(self):
        """Print enrolment count and subject details following the assessment sample."""
        print(f"        Showing {len(self.subjects)} subjects")
        for subject in self.subjects:
            print(f"        [ {subject} ]")

    def __str__(self):
        """Display identity for the admin list without exposing the password."""
        return f"{self.name} :: {self.student_id} --> Email: {self.email}"


## PRE-CANVAS IMPLEMENTATION - retained as ## comments before course-aligned changes.
## """Student entity shared by the student, subject and administrator systems."""
## 
## from validator import Validator
## 
## 
## class Student:
##     """Own a student's identity, credentials and at most four enrolled subjects."""
## 
##     MAX_SUBJECTS = 4
## 
##     def __init__(self, student_id, name, email, password):
##         """Initialise an account with an empty subject list."""
##         self.student_id = str(student_id).zfill(6)
##         self.name = name
##         self.email = email
##         self.password = password
##         self.subjects = []
## 
##     def change_password(self, new_password):
##         """Replace the password only when the shared validation rule accepts it."""
##         if not Validator.validate_password(new_password):
##             raise ValueError(Validator.PASSWORD_HELP)
##         self.password = new_password
## 
##     def can_enrol(self):
##         """Return whether the student's enrolment has space for another subject."""
##         return len(self.subjects) < self.MAX_SUBJECTS
## 
##     def enrol_subject(self, subject):
##         """Add a subject when there is space and its ID is not already enrolled."""
##         if not self.can_enrol() or any(item.subject_id == subject.subject_id for item in self.subjects):
##             return False
##         self.subjects.append(subject)
##         return True
## 
##     def remove_subject(self, subject):
##         """Remove only the requested subject, accepting an object or numeric ID."""
##         try:
##             subject_id = int(getattr(subject, "subject_id", subject))
##         except (ValueError, TypeError):
##             return False
##         for index, enrolled in enumerate(self.subjects):
##             if enrolled.subject_id == subject_id:
##                 del self.subjects[index]
##                 return True
##         return False
## 
##     def get_subjects(self):
##         """Return a separate list for displaying the current enrolment."""
##         return list(self.subjects)
## 
##     def show_subjects(self):
##         """Display enrolment details or an explicit empty-state message in the CLI."""
##         if not self.subjects:
##             print("You have no enrolled subjects.")
##         for subject in self.subjects:
##             print(subject)

## ORIGINAL CODE - retained as requested; active implementation appears above.
## class Student:
##     def __init__(self, student_id, name, email, password):
##         self.student_id = student_id
##         self.name = name
##         self.email = email
##         self.password = password
##         self.subjects = []
## 
##     def change_password(self, new_password):
##         self.password = new_password
## 
##     def enrol_subject(self, subject):
##         if len(self.subjects) < 4:
##             self.subjects.append(subject)
##             return True
##         else:
##             return False
## 
##     def remove_subject(self, subject):
##         for subject in self.subjects:
##             if subject.subject_id == subject.subject_id:
##                 self.subjects.remove(subject)
##                 return True
##         return False
## 
##     def show_subjects(self):
##         for subject in self.subjects:
##             print(subject)
