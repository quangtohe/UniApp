class Student:
    def __init__(self, student_id, name, email, password):
        self.student_id = student_id
        self.name = name
        self.email = email
        self.password = password
        self.subjects = []

    def change_password(self, new_password):
        self.password = new_password

    def enrol_subject(self, subject):
        if len(self.subjects) < 4:
            self.subjects.append(subject)
            return True
        else:
            return False

    def remove_subject(self, subject):
        for subject in self.subjects:
            if subject.subject_id == subject.subject_id:
                self.subjects.remove(subject)
                return True
        return False

    def show_subjects(self):
        for subject in self.subjects:
            print(subject)
