
from subject import Subject
from database import Database


class SubjectController:
    def __init__(self):
        self.database = Database()

    def subject_menu(self, student):
        while True:
            print("\n--- Subject Enrolment System ---")
            print("1. Enrol in a subject")
            print("2. Display enrolled subjects")
            print("3. Remove a subject")
            print("4. Change password")
            print("5. Logout")

            choice = input("Choose an option: ").strip()

            if choice == "1":
                self.enrol_subject(student)
            elif choice == "2":
                student.show_subjects()
            elif choice == "3":
                self.remove_subject(student)
            elif choice == "4":
                self.change_password(student)
            elif choice == "5":
                print("Logged out successfully.")
                break
            else:
                print("Invalid option. Please try again.")

    def enrol_subject(self, student):
        if len(student.subjects) >= 4:
            print("You cannot enrol in more than four subjects.")
            return

        subject = Subject()

        existing_ids = {
            item.subject_id for item in student.subjects
        }

        while subject.subject_id in existing_ids:
            subject = Subject()

        if student.enrol_subject(subject):
            self.save_student(student)
            print("Subject enrolled successfully.")
            print(subject)
        else:
            print("Subject enrolment failed.")

    def remove_subject(self, student):
        if not student.subjects:
            print("You have no enrolled subjects.")
            return

        student.show_subjects()

        try:
            subject_id = int(input("Enter the subject ID to remove: "))
        except ValueError:
            print("Please enter a valid numeric subject ID.")
            return

        for subject in student.subjects:
            if subject.subject_id == subject_id:
                if student.remove_subject(subject):
                    self.save_student(student)
                    print("Subject removed successfully.")
                    return

        print("Subject ID not found.")

    def change_password(self, student):
        new_password = input("Enter your new password: ").strip()

        student.change_password(new_password)
        self.save_student(student)

        print("Password updated successfully.")

    def save_student(self, updated_student):
        students = self.database.read_students()

        for index, student in enumerate(students):
            if student.student_id == updated_student.student_id:
                students[index] = updated_student
                self.database.write_students(students)
                return

        print("Error: Student record not found.")
