from admin_controller import AdminController
from database import Database, DatabaseError
from student_controller import StudentController


class CLIUniApp:
    """Integrate the student and admin subsystems with one shared file database."""

    def __init__(self, database=None):
        """Create controllers against the same database dependency."""
        self.database = database if database is not None else Database()
        self.student_system = StudentController(self.database)
        self.admin_system = AdminController(self.database)

    def run(self):
        """Dispatch A/S/X choices and handle terminal EOF or keyboard interruption."""
        try:
            while True:
                choice = input("University System: (A)dmin, (S)tudent, or X : ").strip().lower()
                if choice in ("s", "1"):
                    self.student_system.student_menu()
                elif choice in ("a", "2"):
                    self.admin_system.admin_menu()
                elif choice in ("x", "3"):
                    print("Thank You")
                    return
                else:
                    print("Invalid option. Please try again.")
        except (EOFError, KeyboardInterrupt):
            print("\nThank You")
        except DatabaseError as error:
            print(error)


## PRE-CANVAS IMPLEMENTATION - retained as ## comments before course-aligned changes.
## """Member 4: top-level university menu integrating the two CLI subsystems."""
## 
## from admin_controller import AdminController
## from database import Database, DatabaseError
## from student_controller import StudentController
## 
## 
## class CLIUniApp:
##     """Wire student and admin menus to the same persistent database."""
## 
##     def __init__(self, database=None):
##         """Construct both subsystems with one database dependency."""
##         self.database = database if database is not None else Database()
##         self.student_system = StudentController(self.database)
##         self.admin_system = AdminController(self.database)
## 
##     def run(self):
##         """Process University Menu selections until exit, EOF or keyboard interrupt."""
##         try:
##             while True:
##                 print("\nUniversity Menu: (s/1) Student System | (a/2) Admin System | (x/3) exit")
##                 choice = input("Choose an option: ").strip().lower()
##                 if choice in ("s", "1"):
##                     self.student_system.student_menu()
##                 elif choice in ("a", "2"):
##                     self.admin_system.admin_menu()
##                 elif choice in ("x", "3"):
##                     print("Goodbye.")
##                     return
##                 else:
##                     print("Invalid option. Please try again.")
##         except (EOFError, KeyboardInterrupt):
##             print("\nGoodbye.")
##         except DatabaseError as error:
##             print(error)
