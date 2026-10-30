"""Member 4: university navigation integrating the existing student and admin menus."""

from admin_controller import AdminController
from database import Database, DatabaseError
from student_controller import StudentController


class CLIUniApp:
    """Connect the A/S/X university menu to Members 1-3 without rewriting their code."""

    def __init__(self, database=None):
        """Share one file with all controllers, including nested legacy constructors."""
        self.database = database if database is not None else Database()
        Database.configure_default(self.database.filename)
        self.student_system = StudentController()
        self.admin_system = AdminController()
        self.student_system.database = self.database
        self.admin_system.database = self.database

    def run(self):
        """Repeat university choices and recover from bad input, EOF or storage errors."""
        try:
            while True:
                choice = input("University System: (A)dmin, (S)tudent, or X : ").strip().lower()
                try:
                    if choice == "a":
                        self.admin_system.admin_menu()
                    elif choice == "s":
                        self.student_system.student_menu()
                    elif choice == "x":
                        print("Thank You")
                        return
                    else:
                        print("Invalid option. Please choose A, S or X.")
                except DatabaseError as error:
                    print(error)
        except (EOFError, KeyboardInterrupt):
            print("\nThank You")
