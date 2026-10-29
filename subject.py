import random
class Subject:
    def __init__(self):
        self.subject_id = random.randint(1,999)
        self.mark = random.randint(25,100)
        self.grade = self.calculate_grade()

    def calculate_grade(self):
        if self.mark >= 85:
            return "HD"
        elif self.mark >= 75:
            return "D"
        elif self.mark >= 65:
            return "C"
        elif self.mark >= 50:
            return "P"
        else:
            return "Z"

    def __str__(self):
        return f"Subject::{self.subject_id:03d} -- mark = {self.mark} -- grade = {self.grade}"