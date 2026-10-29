"""Member 2: enrolment, subject removal and validated password changes."""

import random

from database import Database, DatabaseError
from subject import Subject
from validator import Validator


class SubjectController:
    """Use the latest Student objects in students.data for every enrolment operation."""

    def __init__(self, database=None):
        """Accept the shared application database or a private test/demo file."""
        self.database = database if database is not None else Database()

    def _current_student(self, student):
        """Find the latest account, rejecting a session whose record has been deleted."""
        students = self.database.read_students()
        for index, stored in enumerate(students):
            if stored.student_id == student.student_id:
                return students, index, stored
        raise ValueError("Student record not found. Please log in again.")

    def _commit(self, students, student, stored):
        """Persist first and synchronise the caller's object only after the save succeeds."""
        self.database.write_students(students)
        student.subjects = stored.get_subjects()
        student.password = stored.password

    def enrol_subject(self, student):
        """Create an unused three-digit subject, respecting the persisted four-subject cap."""
        students, index, stored = self._current_student(student)
        if not stored.can_enrol():
            raise ValueError("You cannot enrol in more than four subjects.")
        used = {subject.subject_id for item in students for subject in item.subjects}
        available = [subject_id for subject_id in range(1, 1000) if subject_id not in used]
        if not available:
            raise ValueError("No subject IDs are available. Remove an enrolment before retrying.")
        subject = Subject(subject_id=random.choice(available))
        stored.enrol_subject(subject)
        self._commit(students, student, stored)
        return subject

    def view_enrolment(self, student):
        """Read the latest enrolments; Student calculates the average from these marks."""
        students, index, stored = self._current_student(student)
        student.subjects = stored.get_subjects()
        return student.get_subjects()

    def remove_subject(self, student, subject_id=None):
        """Validate the requested subject ID and persist removal of only that subject."""
        if subject_id is None:
            subject_id = input("        Remove Subject by ID: ").strip()
        try:
            subject_id = int(subject_id)
        except (ValueError, TypeError) as error:
            raise ValueError("Please enter a numeric subject ID between 001 and 999.") from error
        if not 1 <= subject_id <= 999:
            raise ValueError("Subject ID must be between 001 and 999.")
        students, index, stored = self._current_student(student)
        if not stored.remove_subject(subject_id):
            raise ValueError("Subject ID not found in your enrolment.")
        self._commit(students, student, stored)
        return True

    def change_password(self, student, new_password=None, confirmation=None):
        """Validate and confirm CLI passwords; explicit service calls may pass a confirmation."""
        if new_password is None:
            print("        Updating Password")
            new_password = input("        New Password: ")
            while not Validator.validate_password(new_password):
                print(f"        {Validator.PASSWORD_HELP}")
                new_password = input("        New Password: ")
            confirmation = input("        Confirm Password: ")
            while confirmation != new_password:
                print("        Password does not match - try again")
                confirmation = input("        Confirm Password: ")
        if not Validator.validate_password(new_password):
            raise ValueError(Validator.PASSWORD_HELP)
        if confirmation is not None and confirmation != new_password:
            raise ValueError("Password does not match - try again")
        students, index, stored = self._current_student(student)
        stored.change_password(new_password)
        self._commit(students, student, stored)
        return True

    def save_student(self, updated_student):
        """Persist an existing student for compatibility with the team's earlier API."""
        students, index, stored = self._current_student(updated_student)
        students[index] = updated_student
        self.database.write_students(students)

    def subject_menu(self, student):
        """Run c/e/r/s/x choices with indentation and wording from the sample output."""
        while True:
            choice = input("        Student Course Menu (c/e/r/s/x): ").strip().lower()
            try:
                if choice in ("c", "p", "4"):
                    self.change_password(student)
                elif choice in ("e", "1"):
                    subject = self.enrol_subject(student)
                    print(f"        Enrolling in Subject-{subject.subject_id:03d}")
                    print(f"        You are now enrolled in {len(student.subjects)} out of 4 subjects")
                elif choice in ("s", "2"):
                    self.view_enrolment(student)
                    student.show_subjects()
                elif choice in ("r", "3"):
                    subject_id = input("        Remove Subject by ID: ").strip()
                    self.remove_subject(student, subject_id)
                    print(f"        Dropping Subject-{int(subject_id):03d}")
                    print(f"        You are now enrolled in {len(student.subjects)} out of 4 subjects")
                elif choice in ("x", "5"):
                    return
                else:
                    print("        Invalid option. Please try again.")
            except (ValueError, DatabaseError) as error:
                if choice in ("e", "1") and "four subjects" in str(error):
                    print("        Students are allowed to enrol in 4 subjects only")
                else:
                    print(f"        {error}")


## PRE-CANVAS IMPLEMENTATION - retained as ## comments before course-aligned changes.
## """Member 2: subject enrolment and password management shared by both interfaces."""
## 
## import random
## 
## from database import Database, DatabaseError
## from subject import Subject
## from validator import Validator
## 
## 
## class SubjectController:
##     """Apply enrolment rules and persist changes using the latest stored student."""
## 
##     def __init__(self, database=None):
##         """Use the shared application database or a supplied test database."""
##         self.database = database if database is not None else Database()
## 
##     def _current_student(self, student):
##         """Load the latest account and reject a student deleted by the administrator."""
##         students = self.database.read_students()
##         for index, stored in enumerate(students):
##             if stored.student_id == student.student_id:
##                 return students, index, stored
##         raise ValueError("Student record not found. Please log in again.")
## 
##     def _commit(self, students, student, stored):
##         """Persist first, then update the caller's account after a successful save."""
##         self.database.write_students(students)
##         student.subjects = stored.get_subjects()
##         student.password = stored.password
## 
##     def enrol_subject(self, student):
##         """Create a globally unused subject ID and save it within the four-subject limit."""
##         students, index, stored = self._current_student(student)
##         if not stored.can_enrol():
##             raise ValueError("You cannot enrol in more than four subjects.")
##         used = {subject.subject_id for item in students for subject in item.subjects}
##         available = [subject_id for subject_id in range(1, 1000) if subject_id not in used]
##         if not available:
##             raise ValueError("No subject IDs are available. Remove an enrolment before retrying.")
##         subject = Subject(subject_id=random.choice(available))
##         stored.enrol_subject(subject)
##         self._commit(students, student, stored)
##         return subject
## 
##     def view_enrolment(self, student):
##         """Return the latest enrolment list rather than a stale GUI/CLI copy."""
##         students, index, stored = self._current_student(student)
##         student.subjects = stored.get_subjects()
##         return student.get_subjects()
## 
##     def remove_subject(self, student, subject_id=None):
##         """Remove the selected ID, optionally prompting when called by legacy CLI code."""
##         if subject_id is None:
##             subject_id = input("Enter the subject ID to remove: ").strip()
##         try:
##             subject_id = int(subject_id)
##         except (TypeError, ValueError) as error:
##             raise ValueError("Please enter a numeric subject ID between 001 and 999.") from error
##         if not 1 <= subject_id <= 999:
##             raise ValueError("Subject ID must be between 001 and 999.")
##         students, index, stored = self._current_student(student)
##         if not stored.remove_subject(subject_id):
##             raise ValueError("Subject ID not found in your enrolment.")
##         self._commit(students, student, stored)
##         return True
## 
##     def change_password(self, student, new_password=None):
##         """Validate and save a new password without stripping significant characters."""
##         if new_password is None:
##             new_password = input("Enter your new password: ")
##         if not Validator.validate_password(new_password):
##             raise ValueError(Validator.PASSWORD_HELP)
##         students, index, stored = self._current_student(student)
##         stored.change_password(new_password)
##         self._commit(students, student, stored)
##         return True
## 
##     def save_student(self, updated_student):
##         """Persist an existing account for compatibility with earlier member code."""
##         students, index, stored = self._current_student(updated_student)
##         students[index] = updated_student
##         self.database.write_students(students)
## 
##     def subject_menu(self, student):
##         """Run enrol/view/remove/password actions until logout, handling user errors."""
##         while True:
##             print("\nSubject Enrolment System")
##             print("(e/1) enrol | (s/2) show | (r/3) remove | (p/4) password | (x/5) logout")
##             choice = input("Choose an option: ").strip().lower()
##             try:
##                 if choice in ("e", "1"):
##                     print("Subject enrolled successfully.", self.enrol_subject(student))
##                 elif choice in ("s", "2"):
##                     self.view_enrolment(student)
##                     student.show_subjects()
##                 elif choice in ("r", "3"):
##                     self.remove_subject(student)
##                     print("Subject removed successfully.")
##                 elif choice in ("p", "4"):
##                     self.change_password(student)
##                     print("Password updated successfully.")
##                 elif choice in ("x", "5"):
##                     print("Logged out successfully.")
##                     return
##                 else:
##                     print("Invalid option. Please try again.")
##             except (ValueError, DatabaseError) as error:
##                 print(error)

## ORIGINAL CODE - retained as requested; active implementation appears above.
## 
## from subject import Subject
## from database import Database
## 
## 
## class SubjectController:
##     def __init__(self):
##         self.database = Database()
## 
##     def subject_menu(self, student):
##         while True:
##             print("\n--- Subject Enrolment System ---")
##             print("1. Enrol in a subject")
##             print("2. Display enrolled subjects")
##             print("3. Remove a subject")
##             print("4. Change password")
##             print("5. Logout")
## 
##             choice = input("Choose an option: ").strip()
## 
##             if choice == "1":
##                 self.enrol_subject(student)
##             elif choice == "2":
##                 student.show_subjects()
##             elif choice == "3":
##                 self.remove_subject(student)
##             elif choice == "4":
##                 self.change_password(student)
##             elif choice == "5":
##                 print("Logged out successfully.")
##                 break
##             else:
##                 print("Invalid option. Please try again.")
## 
##     def enrol_subject(self, student):
##         if len(student.subjects) >= 4:
##             print("You cannot enrol in more than four subjects.")
##             return
## 
##         subject = Subject()
## 
##         existing_ids = {
##             item.subject_id for item in student.subjects
##         }
## 
##         while subject.subject_id in existing_ids:
##             subject = Subject()
## 
##         if student.enrol_subject(subject):
##             self.save_student(student)
##             print("Subject enrolled successfully.")
##             print(subject)
##         else:
##             print("Subject enrolment failed.")
## 
##     def remove_subject(self, student):
##         if not student.subjects:
##             print("You have no enrolled subjects.")
##             return
## 
##         student.show_subjects()
## 
##         try:
##             subject_id = int(input("Enter the subject ID to remove: "))
##         except ValueError:
##             print("Please enter a valid numeric subject ID.")
##             return
## 
##         for subject in student.subjects:
##             if subject.subject_id == subject_id:
##                 if student.remove_subject(subject):
##                     self.save_student(student)
##                     print("Subject removed successfully.")
##                     return
## 
##         print("Subject ID not found.")
## 
##     def change_password(self, student):
##         new_password = input("Enter your new password: ").strip()
## 
##         student.change_password(new_password)
##         self.save_student(student)
## 
##         print("Password updated successfully.")
## 
##     def save_student(self, updated_student):
##         students = self.database.read_students()
## 
##         for index, student in enumerate(students):
##             if student.student_id == updated_student.student_id:
##                 students[index] = updated_student
##                 self.database.write_students(students)
##                 return
## 
##         print("Error: Student record not found.")
