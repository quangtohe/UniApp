"""Member 3: file-backed student reporting and administration."""

from database import Database, DatabaseError
from grade import Grade


class AdminController:
    """Group and partition students by average, as specified in Part 2 pages 3 and 6."""

    def __init__(self, database=None):
        """Use the shared database, or an injected file for tests and demos."""
        self.database = database if database is not None else Database()

    @staticmethod
    def average_mark(student):
        """Delegate average calculation to the entity that owns the subject marks."""
        return student.average_mark()

    @staticmethod
    def grade_from_average(average):
        """Apply the same grade boundaries to an unrounded student average."""
        return Grade.from_mark(average)

    @staticmethod
    def display_student(student):
        """Print the identity record in the form used in the sample Student List."""
        print(f"        {student}")

    def view_all_students(self):
        """Read students from disk in registration order, preserving the sample order."""
        return self.database.read_students()

    def results_by_grade(self):
        """Place each graded student in exactly one group using their average grade."""
        groups = {grade: [] for grade in Grade}
        for student in self.view_all_students():
            grade = student.overall_grade()
            if grade is not None:
                groups[grade].append(student)
        return groups

    def pass_fail_results(self):
        """Partition graded students once: average below 50 FAIL, otherwise PASS."""
        groups = {"FAIL": [], "PASS": []}
        for student in self.view_all_students():
            average = student.average_mark()
            if average is not None:
                groups["PASS" if average >= 50 else "FAIL"].append(student)
        return groups

    def show_all_students(self):
        """Print students from students.data, including the sample's empty-state text."""
        print("        Student List")
        students = self.view_all_students()
        if not students:
            print("            < Nothing to Display >")
        for student in students:
            self.display_student(student)

    @staticmethod
    def _format_group(students):
        """Create a bracketed collection of student average summaries without quotes."""
        return "[" + ", ".join(student.result_summary() for student in students) + "]"

    def _show_ungraded(self):
        """Keep accounts with no enrolled subjects out of PASS/FAIL classifications."""
        students = [student for student in self.view_all_students() if not student.subjects]
        if students:
            print(f"        NOT GRADED --> {self._format_group(students)}")

    def group_students_by_grade(self):
        """Display populated grade groups using each student's current average."""
        print("        Grade Grouping")
        groups = self.results_by_grade()
        if not any(groups.values()):
            print("            < Nothing to Display >")
        for grade, students in groups.items():
            if students:
                print(f"        {grade} --> {self._format_group(students)}")
        self._show_ungraded()

    def partition_pass_fail(self):
        """Print FAIL then PASS, matching the assessment's partition output order."""
        print("        PASS/FAIL Partition")
        for outcome, students in self.pass_fail_results().items():
            print(f"        {outcome} --> {self._format_group(students)}")
        self._show_ungraded()

    def remove_student_by_id(self, student_id):
        """Delete one student and all their enrolments; report an unknown ID as False."""
        students = self.database.read_students()
        remaining = [student for student in students if student.student_id != student_id]
        if len(remaining) == len(students):
            return False
        self.database.write_students(remaining)
        return True

    def remove_student(self):
        """Read the target ID and remove it following the sample remove-by-ID flow."""
        student_id = input("        Remove by ID: ").strip()
        if self.remove_student_by_id(student_id):
            print(f"        Removing Student {student_id} Account")
        else:
            print(f"        Student {student_id} does not exist")

    def clear_all_students(self):
        """Require a Y confirmation before clearing the persisted student objects."""
        print("        Clearing students database")
        confirmation = input("        Are you sure you want to clear the database (Y)ES/(N)O: ").strip().upper()
        if confirmation == "Y":
            self.database.clear_students()
            print("        Students data cleared")
        else:
            print("        Clear cancelled")

    def admin_menu(self):
        """Run the assessment's c/g/p/r/s/x admin menu until returning to university."""
        actions = {"s": self.show_all_students, "1": self.show_all_students,
                   "g": self.group_students_by_grade, "2": self.group_students_by_grade,
                   "p": self.partition_pass_fail, "3": self.partition_pass_fail,
                   "r": self.remove_student, "4": self.remove_student,
                   "c": self.clear_all_students, "5": self.clear_all_students}
        while True:
            choice = input("    Admin System (c/g/p/r/s/x): ").strip().lower()
            if choice in ("x", "6"):
                return
            try:
                if choice in actions:
                    actions[choice]()
                else:
                    print("        Invalid option. Please try again.")
            except (ValueError, DatabaseError) as error:
                print(f"        {error}")


if __name__ == "__main__":
    AdminController().admin_menu()


## PRE-CANVAS IMPLEMENTATION - retained as ## comments before course-aligned changes.
## """Member 3: administrator views and confirmed student-data deletion."""
## 
## from database import Database, DatabaseError
## from grade import Grade
## 
## 
## class AdminController:
##     """Display students and group individual subject results per stories 501-504."""
## 
##     def __init__(self, database=None):
##         """Use the shared application database or a supplied test database."""
##         self.database = database if database is not None else Database()
## 
##     @staticmethod
##     def average_mark(student):
##         """Calculate a supplementary mean, keeping unenrolled students ungraded."""
##         if not student.subjects:
##             return None
##         return sum(subject.mark for subject in student.subjects) / len(student.subjects)
## 
##     @staticmethod
##     def grade_from_average(average):
##         """Map the supplementary mean to the same grade boundaries as subjects."""
##         return Grade.from_mark(average)
## 
##     @staticmethod
##     def display_student(student):
##         """Display the student's identity and every enrolled subject without credentials."""
##         print(f"ID: {student.student_id} | Name: {student.name} | Email: {student.email} | Subjects: {len(student.subjects)}")
##         for subject in student.subjects:
##             print(f"  {subject}")
##         if not student.subjects:
##             print("  Not graded (no subjects).")
## 
##     def view_all_students(self):
##         """Return all students ordered by ID for reporting and integration tests."""
##         return sorted(self.database.read_students(), key=lambda item: item.student_id)
## 
##     def results_by_grade(self):
##         """Group (student, subject) pairs by each subject's own grade."""
##         groups = {grade: [] for grade in Grade}
##         for student in self.view_all_students():
##             for subject in student.subjects:
##                 groups[Grade.from_mark(subject.mark)].append((student, subject))
##         return groups
## 
##     def pass_fail_results(self):
##         """Partition individual results into FAIL below 50 and PASS from 50 upward."""
##         groups = {"PASS": [], "FAIL": []}
##         for student in self.view_all_students():
##             for subject in student.subjects:
##                 groups["PASS" if subject.mark >= 50 else "FAIL"].append((student, subject))
##         return groups
## 
##     def show_all_students(self):
##         """Print all student records including enrolments and an empty-state message."""
##         students = self.view_all_students()
##         print("\n--- All Students ---")
##         if not students:
##             print("No students registered.")
##         for student in students:
##             self.display_student(student)
##         print(f"Total students: {len(students)}")
## 
##     def _display_groups(self, groups):
##         """Print grouped subject results and list accounts that have no results yet."""
##         for title, results in groups.items():
##             print(f"\n--- {title} ({len(results)} results) ---")
##             for student, subject in results:
##                 print(f"{student.student_id} | {student.name} | {subject}")
##         ungraded = [student for student in self.view_all_students() if not student.subjects]
##         print(f"\nNot graded ({len(ungraded)} students)")
##         for student in ungraded:
##             self.display_student(student)
## 
##     def group_students_by_grade(self):
##         """Display grade groups using individual results rather than student averages."""
##         self._display_groups(self.results_by_grade())
## 
##     def partition_pass_fail(self):
##         """Display PASS/FAIL groups with unenrolled students listed separately."""
##         self._display_groups(self.pass_fail_results())
## 
##     def remove_student_by_id(self, student_id):
##         """Delete one account and its owned subjects; return False for an unknown ID."""
##         students = self.database.read_students()
##         remaining = [student for student in students if student.student_id != student_id]
##         if len(remaining) == len(students):
##             return False
##         self.database.write_students(remaining)
##         return True
## 
##     def remove_student(self):
##         """Prompt for an existing student and require y before deleting the record."""
##         student_id = input("Enter six-digit student ID to remove: ").strip()
##         student = self.database.find_student_by_id(student_id)
##         if student is None:
##             print("Student ID not found.")
##             return
##         self.display_student(student)
##         if input("Remove this student? (y/n): ").strip().lower() != "y":
##             print("Removal cancelled.")
##             return
##         self.remove_student_by_id(student_id)
##         print("Student removed successfully.")
## 
##     def clear_all_students(self):
##         """Clear the data file only after an explicit uppercase CLEAR confirmation."""
##         if input("Delete ALL student records? Type CLEAR to confirm: ").strip() != "CLEAR":
##             print("Clear cancelled.")
##             return
##         self.database.clear_students()
##         print("All student records cleared.")
## 
##     def admin_menu(self):
##         """Run administrator actions and return to University Menu on exit."""
##         actions = {"s": self.show_all_students, "1": self.show_all_students,
##                    "g": self.group_students_by_grade, "2": self.group_students_by_grade,
##                    "p": self.partition_pass_fail, "3": self.partition_pass_fail,
##                    "r": self.remove_student, "4": self.remove_student,
##                    "c": self.clear_all_students, "5": self.clear_all_students}
##         while True:
##             print("\nAdmin System")
##             print("(s/1) show | (g/2) grade | (p/3) PASS/FAIL | (r/4) remove | (c/5) clear | (x/6) return")
##             choice = input("Choose an option: ").strip().lower()
##             if choice in ("x", "6"):
##                 return
##             try:
##                 if choice in actions:
##                     actions[choice]()
##                 else:
##                     print("Invalid option. Please try again.")
##             except (ValueError, DatabaseError) as error:
##                 print(error)
## 
## 
## if __name__ == "__main__":
##     AdminController().admin_menu()

## ORIGINAL CODE - retained as requested; active implementation appears above.
## from database import Database
## 
## 
## class AdminController:
##     """Administrative operations for the CLI university application."""
## 
##     def __init__(self):
##         self.database = Database()
## 
##     @staticmethod
##     def average_mark(student):
##         if not student.subjects:
##             return None
##         return sum(subject.mark for subject in student.subjects) / len(student.subjects)
## 
##     @staticmethod
##     def grade_from_average(average):
##         if average >= 85:
##             return "HD"
##         if average >= 75:
##             return "D"
##         if average >= 65:
##             return "C"
##         if average >= 50:
##             return "P"
##         return "Z"
## 
##     @staticmethod
##     def display_student(student):
##         average = AdminController.average_mark(student)
##         result = f"{average:.2f} ({AdminController.grade_from_average(average)})" if average is not None else "N/A (no subjects)"
##         print(f"ID: {student.student_id} | Name: {student.name} | Email: {student.email} | Subjects: {len(student.subjects)} | Average: {result}")
## 
##     def show_all_students(self):
##         students = self.database.read_students()
##         print("\n--- All Students ---")
##         if not students:
##             print("No students registered.")
##             return
##         for student in sorted(students, key=lambda item: item.student_id):
##             self.display_student(student)
##         print(f"Total students: {len(students)}")
## 
##     def group_students_by_grade(self):
##         students = self.database.read_students()
##         groups = {grade: [] for grade in ("HD", "D", "C", "P", "Z")}
##         unenrolled = []
##         for student in students:
##             average = self.average_mark(student)
##             if average is None:
##                 unenrolled.append(student)
##             else:
##                 groups[self.grade_from_average(average)].append(student)
##         print("\n--- Students Grouped by Average Grade ---")
##         for grade, members in groups.items():
##             print(f"\n{grade} ({len(members)} students)")
##             for student in members:
##                 self.display_student(student)
##         print(f"\nNot graded ({len(unenrolled)} students)")
##         for student in unenrolled:
##             self.display_student(student)
## 
##     def partition_pass_fail(self):
##         students = self.database.read_students()
##         passed, failed, ungraded = [], [], []
##         for student in students:
##             average = self.average_mark(student)
##             if average is None:
##                 ungraded.append(student)
##             elif average >= 50:
##                 passed.append(student)
##             else:
##                 failed.append(student)
##         for title, members in (("PASS", passed), ("FAIL", failed), ("NOT GRADED", ungraded)):
##             print(f"\n--- {title} ({len(members)}) ---")
##             for student in members:
##                 self.display_student(student)
## 
##     def remove_student(self):
##         student_id = input("Enter student ID to remove: ").strip()
##         if not student_id:
##             print("Student ID cannot be empty.")
##             return
##         students = self.database.read_students()
##         matching = next((student for student in students if student.student_id == student_id), None)
##         if matching is None:
##             print("Student ID not found.")
##             return
##         self.display_student(matching)
##         confirmation = input("Remove this student? (y/n): ").strip().lower()
##         if confirmation != "y":
##             print("Removal cancelled.")
##             return
##         remaining = [student for student in students if student.student_id != student_id]
##         self.database.write_students(remaining)
##         print("Student removed successfully.")
## 
##     def clear_all_students(self):
##         confirmation = input("Delete ALL student records? Type CLEAR to confirm: ").strip()
##         if confirmation != "CLEAR":
##             print("Clear cancelled.")
##             return
##         self.database.clear_students()
##         print("All student records cleared.")
## 
##     def admin_menu(self):
##         while True:
##             print("\n--- Admin System ---")
##             print("1. Show all students")
##             print("2. Group students by grade")
##             print("3. Partition students into PASS / FAIL")
##             print("4. Remove a student by ID")
##             print("5. Clear all student data")
##             print("6. Exit")
##             choice = input("Choose an option: ").strip()
##             if choice == "1":
##                 self.show_all_students()
##             elif choice == "2":
##                 self.group_students_by_grade()
##             elif choice == "3":
##                 self.partition_pass_fail()
##             elif choice == "4":
##                 self.remove_student()
##             elif choice == "5":
##                 self.clear_all_students()
##             elif choice == "6":
##                 print("Exiting Admin System.")
##                 break
##             else:
##                 print("Invalid option. Please try again.")
## 
## 
## if __name__ == "__main__":
##     AdminController().admin_menu()
