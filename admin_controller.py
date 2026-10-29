from database import Database


class AdminController:
    """Administrative operations for the CLI university application."""

    def __init__(self):
        self.database = Database()

    @staticmethod
    def average_mark(student):
        if not student.subjects:
            return None
        return sum(subject.mark for subject in student.subjects) / len(student.subjects)

    @staticmethod
    def grade_from_average(average):
        if average >= 85:
            return "HD"
        if average >= 75:
            return "D"
        if average >= 65:
            return "C"
        if average >= 50:
            return "P"
        return "Z"

    @staticmethod
    def display_student(student):
        average = AdminController.average_mark(student)
        result = f"{average:.2f} ({AdminController.grade_from_average(average)})" if average is not None else "N/A (no subjects)"
        print(f"ID: {student.student_id} | Name: {student.name} | Email: {student.email} | Subjects: {len(student.subjects)} | Average: {result}")

    def show_all_students(self):
        students = self.database.read_students()
        print("\n--- All Students ---")
        if not students:
            print("No students registered.")
            return
        for student in sorted(students, key=lambda item: item.student_id):
            self.display_student(student)
        print(f"Total students: {len(students)}")

    def group_students_by_grade(self):
        students = self.database.read_students()
        groups = {grade: [] for grade in ("HD", "D", "C", "P", "Z")}
        unenrolled = []
        for student in students:
            average = self.average_mark(student)
            if average is None:
                unenrolled.append(student)
            else:
                groups[self.grade_from_average(average)].append(student)
        print("\n--- Students Grouped by Average Grade ---")
        for grade, members in groups.items():
            print(f"\n{grade} ({len(members)} students)")
            for student in members:
                self.display_student(student)
        print(f"\nNot graded ({len(unenrolled)} students)")
        for student in unenrolled:
            self.display_student(student)

    def partition_pass_fail(self):
        students = self.database.read_students()
        passed, failed, ungraded = [], [], []
        for student in students:
            average = self.average_mark(student)
            if average is None:
                ungraded.append(student)
            elif average >= 50:
                passed.append(student)
            else:
                failed.append(student)
        for title, members in (("PASS", passed), ("FAIL", failed), ("NOT GRADED", ungraded)):
            print(f"\n--- {title} ({len(members)}) ---")
            for student in members:
                self.display_student(student)

    def remove_student(self):
        student_id = input("Enter student ID to remove: ").strip()
        if not student_id:
            print("Student ID cannot be empty.")
            return
        students = self.database.read_students()
        matching = next((student for student in students if student.student_id == student_id), None)
        if matching is None:
            print("Student ID not found.")
            return
        self.display_student(matching)
        confirmation = input("Remove this student? (y/n): ").strip().lower()
        if confirmation != "y":
            print("Removal cancelled.")
            return
        remaining = [student for student in students if student.student_id != student_id]
        self.database.write_students(remaining)
        print("Student removed successfully.")

    def clear_all_students(self):
        confirmation = input("Delete ALL student records? Type CLEAR to confirm: ").strip()
        if confirmation != "CLEAR":
            print("Clear cancelled.")
            return
        self.database.clear_students()
        print("All student records cleared.")

    def admin_menu(self):
        while True:
            print("\n--- Admin System ---")
            print("1. Show all students")
            print("2. Group students by grade")
            print("3. Partition students into PASS / FAIL")
            print("4. Remove a student by ID")
            print("5. Clear all student data")
            print("6. Exit")
            choice = input("Choose an option: ").strip()
            if choice == "1":
                self.show_all_students()
            elif choice == "2":
                self.group_students_by_grade()
            elif choice == "3":
                self.partition_pass_fail()
            elif choice == "4":
                self.remove_student()
            elif choice == "5":
                self.clear_all_students()
            elif choice == "6":
                print("Exiting Admin System.")
                break
            else:
                print("Invalid option. Please try again.")


if __name__ == "__main__":
    AdminController().admin_menu()
