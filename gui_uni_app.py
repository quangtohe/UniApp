"""Student portal views built with standard Tkinter and the shared app controllers."""

import tkinter as tk
from tkinter import ttk

from database import Database, DatabaseError
from student_controller import StudentController
from subject_controller import SubjectController


class PortalTheme:
    """Keep colours, fonts and widget styles consistent across the four windows."""

    BG = "#F3F6FA"
    WHITE = "#FFFFFF"
    NAVY = "#112536"
    NAVY_LIGHT = "#1C374A"
    TEXT = "#152D3E"
    MUTED = "#64788A"
    LINE = "#DFE7EE"
    ACCENT = "#087F78"
    TINT = "#E6F5F1"

    @classmethod
    def apply(cls, root):
        """Use a configurable ttk theme instead of Windows' default grey widget styles."""
        root.configure(background=cls.BG)
        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure(".", font=("Segoe UI", 10), background=cls.BG, foreground=cls.TEXT)
        style.configure("TFrame", background=cls.BG)
        style.configure("Card.TFrame", background=cls.WHITE)
        for name, size, weight, colour, background in (
            ("Title", 25, "bold", cls.TEXT, cls.BG),
            ("Subtitle", 10, "normal", cls.MUTED, cls.BG),
            ("Eyebrow", 9, "bold", cls.ACCENT, cls.BG),
            ("CardTitle", 15, "bold", cls.TEXT, cls.WHITE),
            ("CardBody", 10, "normal", cls.MUTED, cls.WHITE),
            ("Field", 10, "bold", cls.TEXT, cls.WHITE),
            ("MetricLabel", 9, "bold", cls.MUTED, cls.WHITE),
            ("Metric", 28, "bold", cls.TEXT, cls.WHITE),
            ("MetricHelp", 9, "normal", cls.MUTED, cls.WHITE),
        ):
            style.configure(f"{name}.TLabel", font=("Segoe UI", size, weight), foreground=colour, background=background)
        style.configure("Portal.TEntry", fieldbackground=cls.WHITE, foreground=cls.TEXT,
                        bordercolor=cls.LINE, lightcolor=cls.LINE, darkcolor=cls.LINE,
                        padding=(12, 10), insertcolor=cls.TEXT)
        style.map("Portal.TEntry", bordercolor=[("focus", cls.ACCENT)], lightcolor=[("focus", cls.ACCENT)], darkcolor=[("focus", cls.ACCENT)])
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), background=cls.ACCENT,
                        foreground=cls.WHITE, borderwidth=0, padding=(18, 12), focuscolor=cls.ACCENT)
        style.map("Primary.TButton", background=[("pressed", "#055D57"), ("active", "#096C66")], foreground=[("disabled", "#DCEDE9")])
        style.configure("Secondary.TButton", font=("Segoe UI", 10, "bold"), background=cls.WHITE,
                        foreground=cls.TEXT, bordercolor=cls.LINE, lightcolor=cls.LINE,
                        darkcolor=cls.LINE, borderwidth=1, padding=(16, 11))
        style.map("Secondary.TButton", background=[("active", "#EDF4F7"), ("pressed", "#E2ECEF")])
        style.configure("Link.TButton", background=cls.BG, foreground=cls.ACCENT,
                        borderwidth=0, padding=(10, 8), font=("Segoe UI", 10, "bold"))
        style.map("Link.TButton", background=[("active", cls.TINT), ("pressed", "#D3EBE5")])
        style.configure("Card.TCheckbutton", background=cls.WHITE, foreground=cls.MUTED, font=("Segoe UI", 9))
        style.map("Card.TCheckbutton", background=[("active", cls.WHITE)])
        ## style.configure("Portal.Horizontal.TProgressbar", background=cls.ACCENT,
        ##                 troughcolor=cls.TINT, borderwidth=0, lightcolor=cls.ACCENT, darkcolor=cls.ACCENT, thickness=5)
        style.configure("Portal.Horizontal.TProgressbar", background=cls.ACCENT,
                        troughcolor=cls.TINT, borderwidth=0, bordercolor=cls.TINT,
                        troughrelief="flat", lightcolor=cls.ACCENT, darkcolor=cls.ACCENT, thickness=5)
        style.configure("Vertical.TScrollbar", background="#CBD8E1", troughcolor="#F5F8FB",
                        bordercolor=cls.WHITE, arrowcolor=cls.MUTED, lightcolor=cls.LINE,
                        darkcolor=cls.LINE, arrowsize=10)
        style.configure("Portal.Treeview", background=cls.WHITE, fieldbackground=cls.WHITE,
                        foreground=cls.TEXT, rowheight=44, borderwidth=0, font=("Segoe UI", 11))
        style.configure("Portal.Treeview.Heading", background="#EAF0F5", foreground=cls.MUTED,
                        font=("Segoe UI", 9, "bold"), borderwidth=0, padding=(14, 12), relief="flat")
        style.map("Portal.Treeview", background=[("selected", "#DDF1EC")], foreground=[("selected", cls.TEXT)])
        style.map("Portal.Treeview.Heading", background=[("active", "#EAF0F5")])

    @classmethod
    def card(cls, parent, padding=24):
        """Return a white card with a subtle border and consistent interior spacing."""
        ## return tk.Frame(parent, background=cls.WHITE, highlightbackground=cls.LINE,
        ##                 highlightthickness=1, padx=padding, pady=padding)
        return tk.Frame(parent, background=cls.WHITE, highlightbackground=cls.LINE,
                        highlightcolor=cls.LINE, highlightthickness=1, padx=padding, pady=padding)


class PortalSidebar(tk.Frame):
    """Provide the portal's visual identity and student context beside the main view."""

    def __init__(self, parent, student=None, subjects_command=None):
        """Create the university wordmark, section labels and optional student identity."""
        super().__init__(parent, background=PortalTheme.NAVY, width=236)
        self.grid_propagate(False)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)
        brand = tk.Frame(self, background=PortalTheme.NAVY)
        brand.grid(row=0, column=0, sticky="ew", padx=26, pady=(30, 48))
        mark = tk.Canvas(brand, width=36, height=36, background=PortalTheme.NAVY, highlightthickness=0)
        mark.pack(side="left", padx=(0, 10))
        mark.create_rectangle(0, 0, 36, 36, fill="#28B5A3", outline="")
        mark.create_text(18, 18, text="U", fill=PortalTheme.WHITE, font=("Georgia", 21, "bold"))
        tk.Label(brand, text="UNIAPP", background=PortalTheme.NAVY, foreground=PortalTheme.WHITE,
                 font=("Segoe UI", 15, "bold")).pack(side="left")
        tk.Label(self, text="STUDENT WORKSPACE", background=PortalTheme.NAVY, foreground="#829BAE",
                 font=("Segoe UI", 8, "bold"), anchor="w").grid(row=1, column=0, sticky="ew", padx=26, pady=(0, 12))
        nav = tk.Frame(self, background=PortalTheme.NAVY_LIGHT)
        nav.grid(row=2, column=0, sticky="ew", padx=16)
        tk.Frame(nav, background="#39C7B3", width=3).pack(side="left", fill="y")
        tk.Label(nav, text="Overview" if student else "Student access", background=PortalTheme.NAVY_LIGHT,
                 foreground=PortalTheme.WHITE, anchor="w", font=("Segoe UI", 10, "bold"), padx=16, pady=14).pack(fill="x")
        middle = tk.Frame(self, background=PortalTheme.NAVY)
        middle.grid(row=3, column=0, sticky="nsew", padx=26, pady=24)
        if student is None:
            tk.Label(middle, text="Your studies.\nOne place.", justify="left", anchor="w",
                     background=PortalTheme.NAVY, foreground=PortalTheme.WHITE,
                     ## font=("Segoe UI", 24, "bold")).pack(anchor="w", pady=(35, 18))
                     font=("Segoe UI", 20, "bold")).pack(anchor="w", pady=(35, 18))
            tk.Label(middle, text="Enrol in subjects.\nFollow your progress.\nMake your next move.", justify="left",
                     background=PortalTheme.NAVY, foreground="#A7BDCC", font=("Segoe UI", 10),
                     wraplength=185).pack(anchor="w")
        else:
            tk.Button(middle, text="My subjects   /", command=subjects_command, anchor="w", cursor="hand2",
                      background=PortalTheme.NAVY, foreground="#B8CCDA", activebackground=PortalTheme.NAVY_LIGHT,
                      activeforeground=PortalTheme.WHITE, relief="flat", borderwidth=0,
                      font=("Segoe UI", 10), padx=0, pady=8).pack(fill="x")
        footer = tk.Frame(self, background=PortalTheme.NAVY)
        footer.grid(row=4, column=0, sticky="ew", padx=26, pady=26)
        tk.Frame(footer, background="#2B4253", height=1).pack(fill="x", pady=(0, 18))
        if student is not None:
            initials = "".join(part[0] for part in student.name.split()[:2]).upper()
            tk.Label(footer, text=initials, background="#24465A", foreground="#7DE0D0",
                     font=("Segoe UI", 12, "bold"), padx=10, pady=8).pack(anchor="w", pady=(0, 10))
            tk.Label(footer, text=student.name, background=PortalTheme.NAVY, foreground=PortalTheme.WHITE,
                     font=("Segoe UI", 10, "bold"), wraplength=180, justify="left").pack(anchor="w")
            tk.Label(footer, text=f"ID  {student.student_id}", background=PortalTheme.NAVY,
                     foreground="#9CB4C5", font=("Segoe UI", 9)).pack(anchor="w", pady=(4, 0))
        else:
            tk.Label(footer, text="GROUP 07", background=PortalTheme.NAVY, foreground="#A7BDCC",
                     font=("Segoe UI", 9, "bold")).pack(anchor="w")
            tk.Label(footer, text="University Application", background=PortalTheme.NAVY,
                     foreground="#829BAE", font=("Segoe UI", 9)).pack(anchor="w", pady=(4, 0))


class LoginView(ttk.Frame):
    """Present the login form as a focused card beside the portal introduction."""

    def __init__(self, parent, application):
        """Build labelled credential fields, a password visibility control and sign-in action."""
        super().__init__(parent)
        self.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        PortalSidebar(self).grid(row=0, column=0, sticky="nsew")
        main = ttk.Frame(self, padding=(44, 30))
        main.grid(row=0, column=1, sticky="nsew")
        main.columnconfigure(0, weight=1)
        main.rowconfigure(0, weight=1)
        main.rowconfigure(2, weight=1)
        content = ttk.Frame(main)
        content.grid(row=1, column=0, sticky="ew")
        content.columnconfigure(0, weight=1)
        ttk.Label(content, text="YOUR STUDENT PORTAL", style="Eyebrow.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 10))
        ttk.Label(content, text="Welcome back.", style="Title.TLabel").grid(row=1, column=0, sticky="w")
        ttk.Label(content, text="Sign in to continue your university journey.", style="Subtitle.TLabel").grid(row=2, column=0, sticky="w", pady=(8, 26))
        card = PortalTheme.card(content, 28)
        card.grid(row=3, column=0, sticky="ew")
        card.columnconfigure(0, weight=1)
        self.email_var = tk.StringVar(parent)
        self.password_var = tk.StringVar(parent)
        self.show_password_var = tk.BooleanVar(parent, value=False)
        ttk.Label(card, text="University email", style="Field.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 8))
        self.email_entry = ttk.Entry(card, textvariable=self.email_var, style="Portal.TEntry", font=("Segoe UI", 11), width=28)
        self.email_entry.grid(row=1, column=0, sticky="ew", pady=(0, 22))
        ttk.Label(card, text="Password", style="Field.TLabel").grid(row=2, column=0, sticky="w", pady=(0, 8))
        self.password_entry = ttk.Entry(card, textvariable=self.password_var, show="*", style="Portal.TEntry", font=("Segoe UI", 11), width=28)
        self.password_entry.grid(row=3, column=0, sticky="ew", pady=(0, 12))
        ttk.Checkbutton(card, text="Show password", variable=self.show_password_var,
                        command=self.toggle_password, style="Card.TCheckbutton").grid(row=4, column=0, sticky="w", pady=(0, 24))
        self.login_button = ttk.Button(card, text="Sign in  →", command=application.login, style="Primary.TButton")
        self.login_button.grid(row=5, column=0, sticky="ew")
        ttk.Label(content, text="New here? Create your account in the CLI Student System first.",
                  style="Subtitle.TLabel", wraplength=450).grid(row=4, column=0, sticky="w", pady=(22, 0))

    def toggle_password(self):
        """Reveal or mask the password according to the student's checkbox choice."""
        self.password_entry.configure(show="" if self.show_password_var.get() else "*")


class EnrolmentWindow(tk.Toplevel):
    """Display student progress and the primary enrolment actions in an overview."""

    def __init__(self, parent, application):
        """Create a sidebar, summary cards and a clear enrolment action area."""
        super().__init__(parent)
        self.withdraw()
        self.configure(background=PortalTheme.BG)
        self.title("University Application | Enrolment")
        ## self.geometry("1040x640")
        ## self.minsize(940, 610)
        self.geometry("1040x710")
        self.minsize(940, 700)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.protocol("WM_DELETE_WINDOW", application.show_login_window)
        student = application.current_student
        PortalSidebar(self, student, application.show_subject_window).grid(row=0, column=0, sticky="nsew")
        main = ttk.Frame(self, padding=(32, 30))
        main.grid(row=0, column=1, sticky="nsew")
        main.columnconfigure(0, weight=1)
        header = ttk.Frame(main)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="STUDENT PORTAL / OVERVIEW", style="Eyebrow.TLabel").grid(row=0, column=0, sticky="w")
        self.logout_button = ttk.Button(header, text="Log out", command=application.show_login_window, style="Link.TButton")
        self.logout_button.grid(row=0, column=1, rowspan=2, sticky="ne")
        first_name = student.name.split()[0]
        ttk.Label(header, text=f"Hello, {first_name}.", style="Title.TLabel", wraplength=490).grid(row=1, column=0, sticky="w", pady=(12, 0))
        ttk.Label(main, text="Here's your enrolment at a glance.", style="Subtitle.TLabel").grid(row=1, column=0, sticky="w", pady=(8, 26))
        self.count_var = tk.StringVar(self)
        self.average_var = tk.StringVar(self)
        self.enrolled_value_var = tk.StringVar(self)
        self.average_value_var = tk.StringVar(self)
        self.grade_value_var = tk.StringVar(self)
        self.places_var = tk.StringVar(self)
        self.notice_var = tk.StringVar(self)
        metrics = ttk.Frame(main)
        metrics.grid(row=2, column=0, sticky="ew", pady=(0, 24))
        for column, (label, variable, help_text) in enumerate((
            ("ENROLLED", self.enrolled_value_var, None),
            ("AVERAGE MARK", self.average_value_var, "Out of 100"),
            ("OVERALL GRADE", self.grade_value_var, "Your current result"),
        )):
            metrics.columnconfigure(column, weight=1, uniform="metric")
            card = PortalTheme.card(metrics, 18)
            card.grid(row=0, column=column, sticky="nsew", padx=(0 if column == 0 else 6, 0 if column == 2 else 6))
            card.columnconfigure(0, weight=1)
            ttk.Label(card, text=label, style="MetricLabel.TLabel").grid(row=0, column=0, sticky="w")
            ttk.Label(card, textvariable=variable, style="Metric.TLabel").grid(row=1, column=0, sticky="w", pady=(12, 8))
            if help_text is None:
                self.progress = ttk.Progressbar(card, maximum=4, style="Portal.Horizontal.TProgressbar", length=120)
                self.progress.grid(row=2, column=0, sticky="ew", pady=(0, 10))
                ttk.Label(card, textvariable=self.places_var, style="MetricHelp.TLabel").grid(row=3, column=0, sticky="w")
            else:
                ttk.Label(card, text=help_text, style="MetricHelp.TLabel").grid(row=2, column=0, sticky="w", pady=(8, 0))
        actions = PortalTheme.card(main, 24)
        actions.grid(row=3, column=0, sticky="ew")
        actions.columnconfigure(0, weight=1)
        ttk.Label(actions, text="Make your next move", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(actions, text="Add a subject or take a closer look at your results.", style="CardBody.TLabel",
                  wraplength=550).grid(row=1, column=0, sticky="w", pady=(8, 22))
        buttons = tk.Frame(actions, background=PortalTheme.WHITE)
        buttons.grid(row=2, column=0, sticky="w")
        self.enrol_button = ttk.Button(buttons, text="+  Enrol in a subject", command=application.enrol_in_subject, style="Primary.TButton")
        self.enrol_button.pack(side="left", padx=(0, 12))
        self.subjects_button = ttk.Button(buttons, text="View subjects  →", command=application.show_subject_window, style="Secondary.TButton")
        self.subjects_button.pack(side="left")
        notice = tk.Frame(main, background=PortalTheme.TINT, padx=18, pady=14)
        notice.grid(row=4, column=0, sticky="ew", pady=(18, 0))
        tk.Label(notice, textvariable=self.notice_var, background=PortalTheme.TINT, foreground="#28685E",
                 font=("Segoe UI", 9), justify="left", wraplength=600).pack(anchor="w")
        footer = ttk.Frame(main)
        footer.grid(row=5, column=0, sticky="ew", pady=(16, 0))
        footer.columnconfigure(0, weight=1)
        ttk.Label(footer, text="Your progress, one subject at a time.", style="Subtitle.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Button(footer, text="Refresh overview", command=application.refresh_subjects, style="Link.TButton").grid(row=0, column=1, sticky="e")

    def update_summary(self, student):
        """Reflect the latest count, average and overall grade without duplicating model rules."""
        count = len(student.get_subjects())
        average = student.average_mark()
        self.count_var.set(f"Enrolled subjects: {count}/4" + (" - limit reached" if count == 4 else ""))
        self.average_var.set("Average: not graded" if average is None else f"Average: {average:.2f} | Grade: {student.overall_grade()}")
        self.enrolled_value_var.set(f"{count} / 4")
        self.average_value_var.set("—" if average is None else f"{average:.2f}")
        self.grade_value_var.set("—" if average is None else str(student.overall_grade()))
        self.places_var.set("All places filled" if count == 4 else f"{4 - count} places available")
        self.progress.configure(value=count)
        self.notice_var.set("All four places are filled. View your subjects to review your results." if count == 4 else "You can enrol in up to four subjects. Your progress updates as you go.")


class SubjectWindow(tk.Toplevel):
    """Present marks and grades in a spacious, consistently styled results table."""

    def __init__(self, parent, application):
        """Create a records header, striped table, empty state and navigation actions."""
        super().__init__(parent)
        self.withdraw()
        self.configure(background=PortalTheme.BG)
        self.title("University Application | Subjects")
        self.geometry("870x560")
        self.minsize(760, 490)
        self.transient(parent)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.protocol("WM_DELETE_WINDOW", application.close_subject_window)
        banner = tk.Frame(self, background=PortalTheme.NAVY, padx=28, pady=16)
        banner.grid(row=0, column=0, sticky="ew")
        tk.Label(banner, text="UNIAPP", font=("Segoe UI", 12, "bold"), background=PortalTheme.NAVY,
                 foreground=PortalTheme.WHITE).pack(side="left")
        tk.Label(banner, text="ACADEMIC RECORD", font=("Segoe UI", 8, "bold"), background=PortalTheme.NAVY,
                 foreground="#A4C3D4").pack(side="right")
        content = ttk.Frame(self, padding=(28, 24))
        content.grid(row=1, column=0, sticky="nsew")
        content.columnconfigure(0, weight=1)
        content.rowconfigure(3, weight=1)
        ttk.Label(content, text="OVERVIEW / MY SUBJECTS", style="Eyebrow.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 8))
        ttk.Label(content, text="Your subjects", style="Title.TLabel").grid(row=1, column=0, sticky="w")
        self.status_var = tk.StringVar(self)
        ttk.Label(content, textvariable=self.status_var, style="Subtitle.TLabel").grid(row=2, column=0, sticky="w", pady=(8, 22))
        ## table_frame = tk.Frame(content, background=PortalTheme.WHITE, highlightbackground=PortalTheme.LINE, highlightthickness=1)
        table_frame = tk.Frame(content, background=PortalTheme.WHITE, highlightbackground=PortalTheme.LINE,
                               highlightcolor=PortalTheme.LINE, highlightthickness=1)
        table_frame.grid(row=3, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        self.tree = ttk.Treeview(table_frame, columns=("id", "mark", "grade"), show="headings", height=5, style="Portal.Treeview")
        for column, title in (("id", "SUBJECT ID"), ("mark", "MARK / 100"), ("grade", "GRADE")):
            self.tree.heading(column, text=title, anchor="center")
            self.tree.column(column, width=180, minwidth=100, anchor="center")
        self.tree.tag_configure("even", background=PortalTheme.WHITE)
        self.tree.tag_configure("odd", background="#F5F8FB")
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.empty_label = tk.Label(table_frame, text="No subjects yet\n\nEnrol in your first subject to see your results here.",
                                    background=PortalTheme.WHITE, foreground=PortalTheme.MUTED,
                                    font=("Segoe UI", 11), justify="center")
        buttons = ttk.Frame(content)
        buttons.grid(row=4, column=0, sticky="ew", pady=(20, 0))
        ttk.Button(buttons, text="Refresh results", command=application.refresh_subjects, style="Link.TButton").pack(side="left")
        ttk.Button(buttons, text="Back to overview", command=application.close_subject_window, style="Secondary.TButton").pack(side="right")

    def update_subjects(self, subjects):
        """Replace rows with the current records and display a helpful empty state."""
        self.tree.delete(*self.tree.get_children())
        for index, subject in enumerate(subjects):
            self.tree.insert("", "end", values=(f"{subject.subject_id:03d}", subject.mark, str(subject.grade)), tags=("even" if index % 2 == 0 else "odd",))
        if subjects:
            self.empty_label.place_forget()
            self.status_var.set(f"{len(subjects)} enrolled subjects  ·  Your latest marks and grades")
        else:
            self.empty_label.place(relx=0.5, rely=0.55, anchor="center")
            self.status_var.set("No subjects enrolled yet.")


class ExceptionWindow(tk.Toplevel):
    """Display a clear, compact error dialog matching the portal's visual language."""

    def __init__(self, parent, message, close_command):
        """Show the actual error with an accessible acknowledgement button and shortcuts."""
        super().__init__(parent)
        self.withdraw()
        self.title("University Application | Exception")
        self.geometry("480x290")
        self.resizable(False, False)
        self.configure(background=PortalTheme.WHITE)
        self.transient(parent)
        self.close_command = close_command
        self.protocol("WM_DELETE_WINDOW", self.dismiss)
        tk.Frame(self, background="#D98546", height=5).pack(fill="x")
        content = tk.Frame(self, background=PortalTheme.WHITE, padx=28, pady=24)
        content.pack(fill="both", expand=True)
        badge = tk.Canvas(content, width=36, height=36, background=PortalTheme.WHITE, highlightthickness=0)
        badge.pack(anchor="w", pady=(0, 12))
        badge.create_oval(0, 0, 35, 35, fill="#FFF0E3", outline="")
        badge.create_text(18, 18, text="!", fill="#A65D26", font=("Segoe UI", 17, "bold"))
        ttk.Label(content, text="Action needed", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 8))
        self.message_var = tk.StringVar(self, value=message)
        ttk.Label(content, textvariable=self.message_var, style="CardBody.TLabel", wraplength=400, justify="left").pack(anchor="w", fill="x")
        self.ok_button = ttk.Button(content, text="Got it", command=self.dismiss, style="Primary.TButton")
        self.ok_button.pack(side="bottom", anchor="e", pady=(18, 0))
        self.bind("<Escape>", self.dismiss)
        self.bind("<Return>", self.dismiss)

    def dismiss(self, event=None):
        """Acknowledge the error from a button, keyboard shortcut or window close action."""
        self.close_command()


class GUIUniApp:
    """Coordinate the four portal views with the existing shared business services."""

    def __init__(self, root=None, database=None, visible=True):
        """Apply the visual theme, create the login root and initialise session state."""
        self.root = root if root is not None else tk.Tk()
        self.database = database if database is not None else Database()
        self.student_system = StudentController(self.database)
        self.subject_system = SubjectController(self.database)
        self.visible = visible
        self.current_student = None
        self.enrolment_window = None
        self.subject_window = None
        self.exception_window = None
        self.root.title("University Application | Login")
        self.root.geometry("980x650")
        self.root.minsize(880, 620)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        PortalTheme.apply(self.root)
        self.login_view = LoginView(self.root, self)
        self.email_var = self.login_view.email_var
        self.password_var = self.login_view.password_var
        self.login_button = self.login_view.login_button
        self.root.bind("<Return>", self._login_on_return)
        self.show_login_window()

    def _present_window(self, window):
        """Centre each new window once, then show it or keep test windows hidden."""
        if self.visible:
            if not getattr(window, "_portal_positioned", False):
                window.update_idletasks()
                width, height = window.winfo_width(), window.winfo_height()
                if window is self.exception_window:
                    parent = self.enrolment_window if self.enrolment_window is not None else self.root
                    x = parent.winfo_x() + (parent.winfo_width() - width) // 2
                    y = parent.winfo_y() + (parent.winfo_height() - height) // 2
                else:
                    x = (window.winfo_screenwidth() - width) // 2
                    y = (window.winfo_screenheight() - height) // 2 - 24
                window.geometry(f"+{max(0, x)}+{max(0, y)}")
                window._portal_positioned = True
            window.deiconify()
            window.lift()
        else:
            window.withdraw()

    def show_login_window(self):
        """Close session views and restore a clean, masked login form."""
        self.close_exception_window()
        self.close_subject_window()
        if self.enrolment_window is not None:
            self.enrolment_window.destroy()
            self.enrolment_window = None
        self.current_student = None
        self.email_var.set("")
        self.password_var.set("")
        self.login_view.show_password_var.set(False)
        self.login_view.toggle_password()
        self._present_window(self.root)
        self.login_view.email_entry.focus_set()

    def _login_on_return(self, event):
        """Submit the login form on Return only while there is no logged-in student."""
        if self.current_student is None:
            self.login()

    def login(self):
        """Authenticate through StudentController and show the enrolment overview."""
        if self.current_student is not None:
            return True
        try:
            student = self.student_system.authenticate(self.email_var.get(), self.password_var.get())
        except (ValueError, DatabaseError) as error:
            self.display_error(str(error))
            return False
        self.close_exception_window()
        self.current_student = student
        self.password_var.set("")
        return self.show_enrolment_window()

    def show_enrolment_window(self):
        """Open the separate overview window and synchronise it with stored enrolments."""
        if self.current_student is None:
            self.display_error("Please log in before viewing enrolments.")
            return False
        if self.enrolment_window is None:
            self.enrolment_window = EnrolmentWindow(self.root, self)
        self.enrol_button = self.enrolment_window.enrol_button
        self.count_var = self.enrolment_window.count_var
        self.root.withdraw()
        if not self.refresh_subjects():
            return False
        self._present_window(self.enrolment_window)
        return True

    def show_subject_window(self):
        """Open or reuse the subject list and populate it with the latest model data."""
        if self.current_student is None:
            self.display_error("Please log in before viewing subjects.")
            return False
        if not self.refresh_subjects():
            return False
        if self.subject_window is None:
            self.subject_window = SubjectWindow(self.enrolment_window, self)
        self.subject_table = self.subject_window.tree
        self.subject_window.update_subjects(self.current_student.get_subjects())
        self._present_window(self.subject_window)
        return True

    def refresh_subjects(self):
        """Refresh metric cards and any open subject table from the shared database."""
        if self.current_student is None:
            return False
        try:
            subjects = self.subject_system.view_enrolment(self.current_student)
        except (ValueError, DatabaseError) as error:
            self.show_login_window()
            self.display_error(str(error))
            return False
        if self.enrolment_window is not None:
            self.enrolment_window.update_summary(self.current_student)
        if self.subject_window is not None:
            self.subject_window.update_subjects(subjects)
        return True

    def enrol_in_subject(self):
        """Enrol through the existing controller and display any rejected fifth attempt."""
        if self.current_student is None:
            self.display_error("Please log in before enrolling.")
            return False
        try:
            self.subject_system.enrol_subject(self.current_student)
        except (ValueError, DatabaseError) as error:
            self.display_error(str(error))
            return False
        return self.refresh_subjects()

    def close_subject_window(self):
        """Close the results window while preserving the current student session."""
        if self.subject_window is not None:
            self.subject_window.destroy()
            self.subject_window = None

    def close_exception_window(self):
        """Release a modal error grab and remove the current error dialog."""
        if self.exception_window is not None:
            if self.exception_window.grab_current() == self.exception_window:
                self.exception_window.grab_release()
            self.exception_window.destroy()
            self.exception_window = None

    def display_error(self, message):
        """Display one centred error dialog with keyboard access to its acknowledgement."""
        self.close_exception_window()
        parent = self.enrolment_window if self.enrolment_window is not None else self.root
        self.exception_window = ExceptionWindow(parent, message, self.close_exception_window)
        self._present_window(self.exception_window)
        if self.visible:
            self.exception_window.wait_visibility()
            self.exception_window.grab_set()
            self.exception_window.ok_button.focus_set()

    def close(self):
        """Close the application and release all Tk child windows."""
        self.close_exception_window()
        self.root.destroy()

    def run(self):
        """Start the application's single Tk event loop."""
        self.root.mainloop()


## PRE-REDESIGN GUI - retained as requested; refreshed implementation appears above.
## """Member 4: four-window Tkinter MVC client for registered students."""
## 
## import tkinter as tk
## from tkinter import ttk
## 
## from database import Database, DatabaseError
## from student_controller import StudentController
## from subject_controller import SubjectController
## 
## 
## class LoginView(ttk.Frame):
##     """Display credentials on the application's main login window."""
## 
##     def __init__(self, parent, application):
##         """Create entries and bind the login button to the application controller."""
##         super().__init__(parent, padding=28)
##         self.grid(row=0, column=0, sticky="nsew")
##         self.columnconfigure(0, weight=1)
##         self.email_var = tk.StringVar(parent)
##         self.password_var = tk.StringVar(parent)
##         ttk.Label(self, text="University Application", style="Title.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 8))
##         ttk.Label(self, text="Student login", style="Heading.TLabel").grid(row=1, column=0, sticky="w", pady=(0, 22))
##         ttk.Label(self, text="University email").grid(row=2, column=0, sticky="w")
##         self.email_entry = ttk.Entry(self, textvariable=self.email_var)
##         self.email_entry.grid(row=3, column=0, sticky="ew", pady=(5, 14))
##         ttk.Label(self, text="Password").grid(row=4, column=0, sticky="w")
##         ttk.Entry(self, textvariable=self.password_var, show="*").grid(row=5, column=0, sticky="ew", pady=(5, 18))
##         self.login_button = ttk.Button(self, text="Log in", command=application.login)
##         self.login_button.grid(row=6, column=0, sticky="ew")
##         ## ttk.Label(self, text="Register through the CLI Student System before using this application.", wraplength=540).grid(row=7, column=0, sticky="w", pady=(20, 0))
##         ttk.Label(self, text="Register through the CLI Student System before using this application.", wraplength=480).grid(row=7, column=0, sticky="w", pady=(20, 0))
## 
## 
## class EnrolmentWindow(tk.Toplevel):
##     """Provide enrolment actions separately from the login and subject-result windows."""
## 
##     def __init__(self, parent, application):
##         """Build the student summary, enrol/view/refresh buttons and logout action."""
##         super().__init__(parent)
##         self.withdraw()
##         self.title("University Application | Enrolment")
##         self.geometry("660x360")
##         self.minsize(560, 330)
##         self.columnconfigure(0, weight=1)
##         self.rowconfigure(0, weight=1)
##         self.protocol("WM_DELETE_WINDOW", application.show_login_window)
##         content = ttk.Frame(self, padding=28)
##         content.grid(row=0, column=0, sticky="nsew")
##         content.columnconfigure(0, weight=1)
##         student = application.current_student
##         ttk.Label(content, text="Subject enrolment", style="Title.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 10))
##         ttk.Label(content, text=f"{student.name} | Student ID {student.student_id}").grid(row=1, column=0, sticky="w")
##         self.count_var = tk.StringVar(self)
##         self.average_var = tk.StringVar(self)
##         ttk.Label(content, textvariable=self.count_var, style="Heading.TLabel").grid(row=2, column=0, sticky="w", pady=(22, 8))
##         ttk.Label(content, textvariable=self.average_var).grid(row=3, column=0, sticky="w")
##         ## ttk.Label(content, text="View subjects to see the marks and grades of your enrolments.", wraplength=530).grid(row=4, column=0, sticky="w", pady=(14, 18))
##         ttk.Label(content, text="View subjects to see the marks and grades of your enrolments.", wraplength=480).grid(row=4, column=0, sticky="w", pady=(14, 18))
##         buttons = ttk.Frame(content)
##         buttons.grid(row=5, column=0, sticky="ew")
##         self.enrol_button = ttk.Button(buttons, text="Enrol in a subject", command=application.enrol_in_subject)
##         self.enrol_button.pack(side="left")
##         self.subjects_button = ttk.Button(buttons, text="View subjects", command=application.show_subject_window)
##         self.subjects_button.pack(side="left", padx=8)
##         ttk.Button(buttons, text="Refresh", command=application.refresh_subjects).pack(side="left")
##         self.logout_button = ttk.Button(content, text="Log out", command=application.show_login_window)
##         self.logout_button.grid(row=6, column=0, sticky="e", pady=(18, 0))
## 
##     def update_summary(self, student):
##         """Reflect the model's latest enrolment count and unrounded average grade."""
##         count = len(student.get_subjects())
##         self.count_var.set(f"Enrolled subjects: {count}/4" + (" - limit reached" if count == 4 else ""))
##         average = student.average_mark()
##         self.average_var.set("Average: not graded" if average is None else f"Average: {average:.2f} | Grade: {student.overall_grade()}")
## 
## 
## class SubjectWindow(tk.Toplevel):
##     """List enrolled subjects with their IDs, marks and grades in a dedicated window."""
## 
##     def __init__(self, parent, application):
##         """Create a resizable results table and refresh/close controls."""
##         super().__init__(parent)
##         self.withdraw()
##         self.title("University Application | Subjects")
##         self.geometry("660x400")
##         self.minsize(520, 340)
##         self.transient(parent)
##         self.columnconfigure(0, weight=1)
##         self.rowconfigure(0, weight=1)
##         self.protocol("WM_DELETE_WINDOW", application.close_subject_window)
##         content = ttk.Frame(self, padding=24)
##         content.grid(row=0, column=0, sticky="nsew")
##         content.columnconfigure(0, weight=1)
##         content.rowconfigure(2, weight=1)
##         ttk.Label(content, text="Enrolled subjects", style="Title.TLabel").grid(row=0, column=0, sticky="w")
##         self.status_var = tk.StringVar(self)
##         ttk.Label(content, textvariable=self.status_var).grid(row=1, column=0, sticky="w", pady=(8, 14))
##         table_frame = ttk.Frame(content)
##         table_frame.grid(row=2, column=0, sticky="nsew")
##         table_frame.columnconfigure(0, weight=1)
##         table_frame.rowconfigure(0, weight=1)
##         self.tree = ttk.Treeview(table_frame, columns=("id", "mark", "grade"), show="headings", height=7)
##         for column, title in (("id", "Subject ID"), ("mark", "Mark"), ("grade", "Grade")):
##             self.tree.heading(column, text=title)
##             self.tree.column(column, width=130, anchor="center")
##         self.tree.grid(row=0, column=0, sticky="nsew")
##         scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
##         scrollbar.grid(row=0, column=1, sticky="ns")
##         self.tree.configure(yscrollcommand=scrollbar.set)
##         buttons = ttk.Frame(content)
##         buttons.grid(row=3, column=0, sticky="ew", pady=(16, 0))
##         ttk.Button(buttons, text="Refresh", command=application.refresh_subjects).pack(side="left")
##         ttk.Button(buttons, text="Close", command=application.close_subject_window).pack(side="right")
## 
##     def update_subjects(self, subjects):
##         """Refresh result rows and explicitly describe an empty enrolment list."""
##         self.tree.delete(*self.tree.get_children())
##         for subject in subjects:
##             self.tree.insert("", "end", values=(f"{subject.subject_id:03d}", subject.mark, str(subject.grade)))
##         self.status_var.set(f"{len(subjects)} enrolled subjects" if subjects else "No subjects enrolled yet.")
## 
## 
## class ExceptionWindow(tk.Toplevel):
##     """Show validation, authentication, storage and enrolment-limit errors."""
## 
##     def __init__(self, parent, message, close_command):
##         """Create an accessible error message and an OK button without blocking tests."""
##         super().__init__(parent)
##         self.withdraw()
##         self.title("University Application | Exception")
##         self.geometry("500x210")
##         self.minsize(420, 190)
##         self.transient(parent)
##         self.protocol("WM_DELETE_WINDOW", close_command)
##         content = ttk.Frame(self, padding=24)
##         content.pack(fill="both", expand=True)
##         ttk.Label(content, text="Unable to complete action", style="Heading.TLabel").pack(anchor="w", pady=(0, 12))
##         self.message_var = tk.StringVar(self, value=message)
##         ## ttk.Label(content, textvariable=self.message_var, wraplength=440).pack(anchor="w", fill="x")
##         ttk.Label(content, textvariable=self.message_var, wraplength=340).pack(anchor="w", fill="x")
##         self.ok_button = ttk.Button(content, text="OK", command=close_command)
##         self.ok_button.pack(side="bottom", anchor="e", pady=(16, 0))
## 
## 
## class GUIUniApp:
##     """Coordinate Tkinter views with the same account/enrolment services as the CLI."""
## 
##     def __init__(self, root=None, database=None, visible=True):
##         """Initialise the root login window; visible=False keeps real test widgets hidden."""
##         self.root = root if root is not None else tk.Tk()
##         self.database = database if database is not None else Database()
##         self.student_system = StudentController(self.database)
##         self.subject_system = SubjectController(self.database)
##         self.visible = visible
##         self.current_student = None
##         self.enrolment_window = None
##         self.subject_window = None
##         self.exception_window = None
##         self.root.title("University Application | Login")
##         self.root.geometry("660x440")
##         self.root.minsize(560, 400)
##         self.root.columnconfigure(0, weight=1)
##         self.root.rowconfigure(0, weight=1)
##         self.root.protocol("WM_DELETE_WINDOW", self.close)
##         style = ttk.Style(self.root)
##         style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"))
##         style.configure("Heading.TLabel", font=("Segoe UI", 11, "bold"))
##         self.login_view = LoginView(self.root, self)
##         self.email_var = self.login_view.email_var
##         self.password_var = self.login_view.password_var
##         self.login_button = self.login_view.login_button
##         self.root.bind("<Return>", self._login_on_return)
##         self.show_login_window()
## 
##     def _present_window(self, window):
##         """Show a live window or keep it withdrawn when running hidden widget tests."""
##         if self.visible:
##             window.deiconify()
##             window.lift()
##         else:
##             window.withdraw()
## 
##     def show_login_window(self):
##         """Log out, close child windows and clear credentials before restoring login."""
##         self.close_exception_window()
##         self.close_subject_window()
##         if self.enrolment_window is not None:
##             self.enrolment_window.destroy()
##             self.enrolment_window = None
##         self.current_student = None
##         self.email_var.set("")
##         self.password_var.set("")
##         self._present_window(self.root)
##         self.login_view.email_entry.focus_set()
## 
##     def _login_on_return(self, event):
##         """Allow Return to submit the login form only while logged out."""
##         if self.current_student is None:
##             self.login()
## 
##     def login(self):
##         """Authenticate from students.data and transition to the enrolment window."""
##         if self.current_student is not None:
##             return True
##         try:
##             student = self.student_system.authenticate(self.email_var.get(), self.password_var.get())
##         except (ValueError, DatabaseError) as error:
##             self.display_error(str(error))
##             return False
##         self.close_exception_window()
##         self.current_student = student
##         self.password_var.set("")
##         return self.show_enrolment_window()
## 
##     def show_enrolment_window(self):
##         """Create the enrolment Toplevel while retaining the root as the login window."""
##         if self.current_student is None:
##             self.display_error("Please log in before viewing enrolments.")
##             return False
##         if self.enrolment_window is None:
##             self.enrolment_window = EnrolmentWindow(self.root, self)
##         self.enrol_button = self.enrolment_window.enrol_button
##         self.count_var = self.enrolment_window.count_var
##         self.root.withdraw()
##         if not self.refresh_subjects():
##             return False
##         self._present_window(self.enrolment_window)
##         return True
## 
##     def show_subject_window(self):
##         """Open or reuse the dedicated subject window and load fresh persisted results."""
##         if self.current_student is None:
##             self.display_error("Please log in before viewing subjects.")
##             return False
##         if not self.refresh_subjects():
##             return False
##         if self.subject_window is None:
##             self.subject_window = SubjectWindow(self.enrolment_window, self)
##         self.subject_table = self.subject_window.tree
##         self.subject_window.update_subjects(self.current_student.get_subjects())
##         self._present_window(self.subject_window)
##         return True
## 
##     def refresh_subjects(self):
##         """Refresh the enrolment summary and any open result table from the shared model."""
##         if self.current_student is None:
##             return False
##         try:
##             subjects = self.subject_system.view_enrolment(self.current_student)
##         except (ValueError, DatabaseError) as error:
##             self.show_login_window()
##             self.display_error(str(error))
##             return False
##         if self.enrolment_window is not None:
##             self.enrolment_window.update_summary(self.current_student)
##         if self.subject_window is not None:
##             self.subject_window.update_subjects(subjects)
##         return True
## 
##     def enrol_in_subject(self):
##         """Persist a new subject or display the fourth-window error on a fifth attempt."""
##         if self.current_student is None:
##             self.display_error("Please log in before enrolling.")
##             return False
##         try:
##             self.subject_system.enrol_subject(self.current_student)
##         except (ValueError, DatabaseError) as error:
##             self.display_error(str(error))
##             return False
##         return self.refresh_subjects()
## 
##     def close_subject_window(self):
##         """Close the result view without logging the student out of enrolment."""
##         if self.subject_window is not None:
##             self.subject_window.destroy()
##             self.subject_window = None
## 
##     def close_exception_window(self):
##         """Release a modal error grab and discard the previous exception window."""
##         if self.exception_window is not None:
##             if self.exception_window.grab_current() == self.exception_window:
##                 self.exception_window.grab_release()
##             self.exception_window.destroy()
##             self.exception_window = None
## 
##     def display_error(self, message):
##         """Show one exception window, modal during interactive use and hidden in tests."""
##         self.close_exception_window()
##         parent = self.enrolment_window if self.enrolment_window is not None else self.root
##         self.exception_window = ExceptionWindow(parent, message, self.close_exception_window)
##         self._present_window(self.exception_window)
##         if self.visible:
##             self.exception_window.wait_visibility()
##             self.exception_window.grab_set()
##             self.exception_window.ok_button.focus_set()
## 
##     def close(self):
##         """Close all views and terminate the Tk application cleanly."""
##         self.close_exception_window()
##         self.root.destroy()
## 
##     def run(self):
##         """Run the single Tk main loop while child Toplevel windows handle events."""
##         self.root.mainloop()

## PRE-CANVAS IMPLEMENTATION - retained as ## comments before course-aligned changes.
## """Member 4: small Tkinter client for registered-student login and enrolment."""
## 
## import tkinter as tk
## from tkinter import messagebox, ttk
## 
## from database import Database, DatabaseError
## from student_controller import StudentController
## from subject_controller import SubjectController
## 
## 
## class GUIUniApp:
##     """Reuse the CLI's account/enrolment services without duplicating business rules."""
## 
##     def __init__(self, root=None, database=None):
##         """Build a resizable application window and initialise the login screen."""
##         self.root = root if root is not None else tk.Tk()
##         self.database = database if database is not None else Database()
##         self.student_system = StudentController(self.database)
##         self.subject_system = SubjectController(self.database)
##         self.current_student = None
##         self.root.title("Group 7 | University Application")
##         self.root.geometry("760x510")
##         self.root.minsize(640, 440)
##         self.root.columnconfigure(0, weight=1)
##         self.root.rowconfigure(0, weight=1)
##         style = ttk.Style(self.root)
##         style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"))
##         style.configure("Heading.TLabel", font=("Segoe UI", 11, "bold"))
##         self.content = ttk.Frame(self.root, padding=28)
##         self.content.grid(row=0, column=0, sticky="nsew")
##         self.content.columnconfigure(0, weight=1)
##         self.show_login_window()
## 
##     def _clear_content(self):
##         """Destroy the previous screen and remove its Return-key action."""
##         self.root.unbind("<Return>")
##         for widget in self.content.winfo_children():
##             widget.destroy()
## 
##     def show_login_window(self):
##         """Display required email/password fields for an already registered account."""
##         self._clear_content()
##         self.current_student = None
##         ttk.Label(self.content, text="University Application", style="Title.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 8))
##         ttk.Label(self.content, text="Student login", style="Heading.TLabel").grid(row=1, column=0, sticky="w", pady=(0, 22))
##         ttk.Label(self.content, text="University email").grid(row=2, column=0, sticky="w")
##         self.email_var = tk.StringVar(self.root)
##         self.password_var = tk.StringVar(self.root)
##         self.email_entry = ttk.Entry(self.content, textvariable=self.email_var)
##         self.email_entry.grid(row=3, column=0, sticky="ew", pady=(5, 14))
##         ttk.Label(self.content, text="Password").grid(row=4, column=0, sticky="w")
##         ttk.Entry(self.content, textvariable=self.password_var, show="*").grid(row=5, column=0, sticky="ew", pady=(5, 18))
##         self.login_button = ttk.Button(self.content, text="Log in", command=self.login)
##         self.login_button.grid(row=6, column=0, sticky="ew")
##         ttk.Label(self.content, text="New student? Register in the CLI Student System first.", wraplength=550).grid(row=7, column=0, sticky="w", pady=(20, 0))
##         self.email_entry.focus_set()
##         self.root.bind("<Return>", self._login_on_return)
## 
##     def _login_on_return(self, event):
##         """Submit login when Return is pressed in the login form."""
##         self.login()
## 
##     def login(self):
##         """Validate entered credentials, show errors and open enrolment on success."""
##         try:
##             self.current_student = self.student_system.authenticate(self.email_var.get(), self.password_var.get())
##         except (ValueError, DatabaseError) as error:
##             self.display_error(str(error))
##             return False
##         self.password_var.set("")
##         self.show_enrolment_window()
##         return True
## 
##     def show_enrolment_window(self):
##         """Display the logged-in student's identity, result table and enrol/logout actions."""
##         self._clear_content()
##         ttk.Label(self.content, text="Subject enrolment", style="Title.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 8))
##         ttk.Label(self.content, text=f"{self.current_student.name} | Student ID {self.current_student.student_id}").grid(row=1, column=0, sticky="w")
##         self.count_var = tk.StringVar(self.root)
##         ttk.Label(self.content, textvariable=self.count_var, style="Heading.TLabel").grid(row=2, column=0, sticky="w", pady=(18, 10))
##         table_frame = ttk.Frame(self.content)
##         table_frame.grid(row=3, column=0, sticky="nsew")
##         table_frame.columnconfigure(0, weight=1)
##         table_frame.rowconfigure(0, weight=1)
##         self.subject_table = ttk.Treeview(table_frame, columns=("id", "mark", "grade"), show="headings", height=7)
##         for column, title in (("id", "Subject ID"), ("mark", "Mark"), ("grade", "Grade")):
##             self.subject_table.heading(column, text=title)
##             self.subject_table.column(column, width=130, anchor="center")
##         self.subject_table.grid(row=0, column=0, sticky="nsew")
##         scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.subject_table.yview)
##         scrollbar.grid(row=0, column=1, sticky="ns")
##         self.subject_table.configure(yscrollcommand=scrollbar.set)
##         buttons = ttk.Frame(self.content)
##         buttons.grid(row=4, column=0, sticky="ew", pady=(18, 0))
##         self.enrol_button = ttk.Button(buttons, text="Enrol in a subject", command=self.enrol_in_subject)
##         self.enrol_button.pack(side="left")
##         ttk.Button(buttons, text="Refresh", command=self.refresh_subjects).pack(side="left", padx=8)
##         ttk.Button(buttons, text="Log out", command=self.show_login_window).pack(side="right")
##         self.refresh_subjects()
## 
##     def refresh_subjects(self):
##         """Reload persisted results and disable enrolment when four subjects are present."""
##         try:
##             subjects = self.subject_system.view_enrolment(self.current_student)
##         except (ValueError, DatabaseError) as error:
##             self.display_error(str(error))
##             self.show_login_window()
##             return False
##         self.subject_table.delete(*self.subject_table.get_children())
##         for subject in subjects:
##             self.subject_table.insert("", "end", values=(f"{subject.subject_id:03d}", subject.mark, str(subject.grade)))
##         count = len(subjects)
##         self.count_var.set(f"Enrolled subjects: {count}/4" + (" - enrolment limit reached" if count == 4 else ""))
##         self.enrol_button.configure(state="disabled" if count >= 4 else "normal")
##         return True
## 
##     def enrol_in_subject(self):
##         """Create and persist one subject through the shared enrolment controller."""
##         if self.current_student is None:
##             self.display_error("Please log in before enrolling.")
##             return False
##         try:
##             self.subject_system.enrol_subject(self.current_student)
##         except (ValueError, DatabaseError) as error:
##             self.display_error(str(error))
##             return False
##         return self.refresh_subjects()
## 
##     def display_error(self, message):
##         """Present a user-readable modal error attached to this application window."""
##         messagebox.showerror("University Application", message, parent=self.root)
## 
##     def run(self):
##         """Start the Tk event loop after all widgets have been initialised."""
##         self.root.mainloop()
