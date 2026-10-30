"""Student registration form sharing the existing UniApp login theme."""

import tkinter as tk
from tkinter import ttk

from gui_uni_app import PortalSidebar, PortalTheme


class RegistrationWindow(tk.Toplevel):
    """Collect a new Student's identity and confirmed password without creating Admins."""

    def __init__(self, parent, application):
        """Build a compact registration card with validation guidance and cancellation."""
        super().__init__(parent)
        self.withdraw()
        self.application = application
        self.title("University Application | Register")
        self.geometry("980x730")
        self.minsize(940, 700)
        self.configure(background=PortalTheme.BG)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.protocol("WM_DELETE_WINDOW", application.close_registration_window)
        self.bind("<Escape>", self._cancel)
        self.bind("<Return>", self._submit)
        PortalSidebar(self).grid(row=0, column=0, sticky="nsew")
        main = ttk.Frame(self, padding=(36, 30))
        main.grid(row=0, column=1, sticky="nsew")
        main.columnconfigure(0, weight=1)
        main.rowconfigure(0, weight=1)
        main.rowconfigure(2, weight=1)
        content = ttk.Frame(main)
        content.grid(row=1, column=0, sticky="ew")
        content.columnconfigure(0, weight=1)
        ttk.Label(content, text="STUDENT REGISTRATION", style="Eyebrow.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(content, text="Create your account.", style="Title.TLabel").grid(row=1, column=0, sticky="w", pady=(10, 8))
        ttk.Label(content, text="Register, then sign in to start your enrolment.", style="Subtitle.TLabel").grid(row=2, column=0, sticky="w", pady=(0, 24))
        card = PortalTheme.card(content, 24)
        card.grid(row=3, column=0, sticky="ew")
        card.columnconfigure(0, weight=1, uniform="register_field")
        card.columnconfigure(1, weight=1, uniform="register_field")
        self.name_var = tk.StringVar(self)
        self.email_var = tk.StringVar(self)
        self.password_var = tk.StringVar(self)
        self.confirmation_var = tk.StringVar(self)
        self.show_password_var = tk.BooleanVar(self, value=False)
        self.entries = {}
        for key, label, variable, row, column, secret in (
            ("name", "Full name", self.name_var, 0, 0, False),
            ("email", "University email", self.email_var, 0, 1, False),
            ("password", "Password", self.password_var, 2, 0, True),
            ("confirmation", "Confirm password", self.confirmation_var, 2, 1, True),
        ):
            padding = (0, 10) if column == 0 else (10, 0)
            ttk.Label(card, text=label, style="Field.TLabel").grid(row=row, column=column, sticky="w", padx=padding, pady=(0, 8))
            entry = ttk.Entry(card, textvariable=variable, show="*" if secret else "", style="Portal.TEntry", width=18, font=("Segoe UI", 11))
            entry.grid(row=row + 1, column=column, sticky="ew", padx=padding, pady=(0, 20))
            self.entries[key] = entry
        ttk.Checkbutton(card, text="Show passwords", variable=self.show_password_var,
                        command=self.toggle_password, style="Card.TCheckbutton").grid(row=4, column=0, columnspan=2, sticky="w", pady=(0, 18))
        ttk.Label(card, text="Email: yourname@university.com\nPassword: uppercase first letter, at least 5 letters, then 3 or more digits. Example: Abcde123",
                  style="CardBody.TLabel", wraplength=540, justify="left").grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0, 24))
        self.cancel_button = ttk.Button(card, text="Back to sign in", command=application.close_registration_window, style="Secondary.TButton")
        self.cancel_button.grid(row=6, column=0, sticky="ew", padx=(0, 10))
        self.register_button = ttk.Button(card, text="Create account  →", command=application.register_student, style="Primary.TButton")
        self.register_button.grid(row=6, column=1, sticky="ew", padx=(10, 0))

    def toggle_password(self):
        """Reveal or mask both password fields together."""
        for key in ("password", "confirmation"):
            self.entries[key].configure(show="" if self.show_password_var.get() else "*")

    def _submit(self, event):
        """Submit registration on Return and stop additional key handling."""
        self.application.register_student()
        return "break"

    def _cancel(self, event):
        """Discard the form on Escape without saving a Student."""
        self.application.close_registration_window()
        return "break"

    def clear_fields(self):
        """Discard typed identity and secret values before closing the form."""
        for variable in (self.name_var, self.email_var, self.password_var, self.confirmation_var):
            variable.set("")
