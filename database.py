import os
import pickle

class Database:
    def __init__(self):
        current_folder = os.path.dirname(__file__)
        self.filename = os.path.join(current_folder, "students.data")
        self.create_file()

    def create_file(self):
        if not os.path.exists(self.filename) or os.path.getsize(self.filename) == 0:
            with open(self.filename, "wb") as file:
                pickle.dump([], file)

    def read_students(self):
        with open(self.filename, "rb") as file:
            return pickle.load(file)

    def write_students(self, students):
        with open(self.filename, "wb") as file:
            pickle.dump(students, file)

    def clear_students(self):
        self.write_students([])