"""Administrator dashboard and confirmation dialogs sharing the UniApp portal theme."""

from functools import partial
import tkinter as tk
from tkinter import ttk

from database import DatabaseError
from gui_uni_app import PortalTheme, PortalSidebar


class AdminConfirmationWindow(tk.Toplevel):
    """Make account removal and clearing records explicit, cancellable GUI actions."""

    def __init__(self, parent, application, title, message, action, phrase=None):
        """Build a confirmation message, optional typed phrase and cancel/confirm buttons."""
        super().__init__(parent)
        self.withdraw()
        self.title(f"University Application | {title}")
        self.geometry("530x330")
        self.resizable(False, False)
        self.configure(background=PortalTheme.WHITE)
        self.transient(parent)
        self.application = application
        self.action = action
        self.required_phrase = phrase
        self.protocol("WM_DELETE_WINDOW", application.close_confirmation_window)
        tk.Frame(self, height=5, background="#B83D49").pack(fill="x")
        content = tk.Frame(self, background=PortalTheme.WHITE, padx=28, pady=24)
        content.pack(fill="both", expand=True)
        ttk.Label(content, text=title, style="CardTitle.TLabel").pack(anchor="w", pady=(0, 12))
        ttk.Label(content, text=message, style="CardBody.TLabel", wraplength=470, justify="left").pack(anchor="w", fill="x")
        self.phrase_var = tk.StringVar(self)
        self.phrase_entry = None
        if phrase is not None:
            ttk.Label(content, text=f"Type {phrase} to confirm", style="Field.TLabel").pack(anchor="w", pady=(18, 8))
            self.phrase_entry = ttk.Entry(content, textvariable=self.phrase_var, style="Portal.TEntry")
            self.phrase_entry.pack(fill="x")
            self.phrase_var.trace_add("write", self._phrase_changed)
        buttons = tk.Frame(content, background=PortalTheme.WHITE)
        buttons.pack(side="bottom", fill="x", pady=(20, 0))
        self.cancel_button = ttk.Button(buttons, text="Cancel", command=application.close_confirmation_window, style="Secondary.TButton")
        self.cancel_button.pack(side="right", padx=(12, 0))
        self.confirm_button = ttk.Button(buttons, text="Clear all records" if phrase else "Remove student", command=self.confirm, style="Danger.TButton")
        self.confirm_button.pack(side="right")
        if phrase:
            self.confirm_button.configure(state="disabled")
        self.bind("<Escape>", self.cancel)

    def _phrase_changed(self, *arguments):
        """Enable clear only when the entered phrase exactly matches the required text."""
        state = "normal" if self.phrase_var.get() == self.required_phrase else "disabled"
        self.confirm_button.configure(state=state)

    def cancel(self, event=None):
        """Dismiss a destructive action without changing the database."""
        self.application.close_confirmation_window()

    def confirm(self):
        """Check the phrase again, close the dialog and execute the approved action."""
        if self.required_phrase and self.phrase_var.get() != self.required_phrase:
            return False
        action = self.action
        self.application.close_confirmation_window()
        return action()


class AdminWindow(tk.Toplevel):
    """Present student records, grade groups, PASS/FAIL and controlled data management."""

    VIEW_MODES = {"All students": "all", "Group by grade": "grade", "PASS / FAIL": "pass_fail"}

    def __init__(self, parent, application):
        """Build the administrator workspace with metrics, filters, records and actions."""
        super().__init__(parent)
        self.withdraw()
        self.application = application
        self.configure(background=PortalTheme.BG)
        self.title("University Application | Administration")
        self.geometry("1260x760")
        self.minsize(1120, 710)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.protocol("WM_DELETE_WINDOW", application.show_login_window)
        PortalSidebar(self, student=application.current_admin, role="admin").grid(row=0, column=0, sticky="nsew")
        main = ttk.Frame(self, padding=(28, 26))
        main.grid(row=0, column=1, sticky="nsew")
        main.columnconfigure(0, weight=1)
        main.rowconfigure(4, weight=1)
        header = ttk.Frame(main)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="ADMINISTRATION / STUDENT RECORDS", style="Eyebrow.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(header, text="Manage students", style="Title.TLabel").grid(row=1, column=0, sticky="w", pady=(10, 0))
        self.logout_button = ttk.Button(header, text="Log out", command=application.show_login_window, style="Link.TButton")
        self.logout_button.grid(row=0, column=1, rowspan=2, sticky="ne")
        ttk.Label(main, text="Review enrolments, organise results and manage student records.", style="Subtitle.TLabel").grid(row=1, column=0, sticky="w", pady=(8, 22))
        metrics = ttk.Frame(main)
        metrics.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        self.metric_vars = {}
        for index, (key, label) in enumerate((("students", "TOTAL STUDENTS"), ("enrolments", "ENROLMENTS"), ("passed", "PASS"), ("failed", "FAIL"))):
            metrics.columnconfigure(index, weight=1, uniform="admin_metric")
            card = PortalTheme.card(metrics, 16)
            card.grid(row=0, column=index, sticky="nsew", padx=(0 if index == 0 else 5, 0 if index == 3 else 5))
            self.metric_vars[key] = tk.StringVar(self, value="0")
            ttk.Label(card, text=label, style="MetricLabel.TLabel").pack(anchor="w")
            ttk.Label(card, textvariable=self.metric_vars[key], style="Metric.TLabel").pack(anchor="w", pady=(8, 0))
        toolbar = PortalTheme.card(main, 14)
        toolbar.grid(row=3, column=0, sticky="ew", pady=(0, 16))
        toolbar.columnconfigure(1, weight=1)
        ttk.Label(toolbar, text="Search", style="Field.TLabel").grid(row=0, column=0, padx=(0, 10))
        self.search_var = tk.StringVar(self)
        self.search_entry = ttk.Entry(toolbar, textvariable=self.search_var, style="Portal.TEntry", width=22)
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 18))
        self.search_entry.bind("<KeyRelease>", self.refresh_students)
        self.view_var = tk.StringVar(self, value="All students")
        self.view_selector = ttk.Combobox(toolbar, textvariable=self.view_var, values=tuple(self.VIEW_MODES), state="readonly", width=17)
        self.view_selector.grid(row=0, column=2, padx=(0, 12))
        self.view_selector.bind("<<ComboboxSelected>>", self.refresh_students)
        self.refresh_button = ttk.Button(toolbar, text="Refresh", command=self.refresh_students, style="Secondary.TButton")
        self.refresh_button.grid(row=0, column=3)
        table_frame = tk.Frame(main, background=PortalTheme.WHITE, highlightthickness=1, highlightbackground=PortalTheme.LINE, highlightcolor=PortalTheme.LINE)
        table_frame.grid(row=4, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        columns = ("id", "name", "email", "subjects", "average", "grade", "result")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse", style="Portal.Treeview")
        for column, title, width in (("id", "ID", 80), ("name", "NAME", 140), ("email", "EMAIL", 210), ("subjects", "SUBJECTS", 80), ("average", "AVERAGE", 90), ("grade", "GRADE", 65), ("result", "RESULT", 105)):
            self.tree.heading(column, text=title)
            self.tree.column(column, width=width, minwidth=60, anchor="w" if column in ("name", "email") else "center")
        self.tree.heading("#0", text="GROUP")
        self.tree.column("#0", width=130, minwidth=110)
        self.tree.tag_configure("even", background=PortalTheme.WHITE)
        self.tree.tag_configure("odd", background="#F5F8FB")
        self.tree.tag_configure("group", background="#E6F5F1", foreground=PortalTheme.ACCENT, font=("Segoe UI", 10, "bold"))
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self._selection_changed)
        vertical = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        horizontal.grid(row=1, column=0, sticky="ew")
        self.tree.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        self.empty_label = tk.Label(table_frame, text="No student records", background=PortalTheme.WHITE, foreground=PortalTheme.MUTED, font=("Segoe UI", 12))
        self.status_var = tk.StringVar(self)
        ttk.Label(main, textvariable=self.status_var, style="Subtitle.TLabel").grid(row=5, column=0, sticky="w", pady=(12, 0))
        actions = ttk.Frame(main)
        actions.grid(row=6, column=0, sticky="ew", pady=(14, 0))
        actions.columnconfigure(0, weight=1)
        self.clear_button = ttk.Button(actions, text="Clear all records", command=self.request_clear, style="DangerOutline.TButton")
        self.clear_button.grid(row=0, column=0, sticky="w")
        self.remove_button = ttk.Button(actions, text="Remove selected student", command=self.request_remove, style="Danger.TButton", state="disabled")
        self.remove_button.grid(row=0, column=1, sticky="e")
        self._rows = {}

    def refresh_students(self, event=None, message=None):
        """Reload persisted records, update metrics and render the selected grouping."""
        mode = self.VIEW_MODES.get(self.view_var.get(), "all")
        try:
            report = self.application.admin_service.report(mode, self.search_var.get())
        except (ValueError, PermissionError, DatabaseError) as error:
            self.application.display_error(str(error))
            return False
        for key, variable in self.metric_vars.items():
            variable.set(str(report["summary"][key]))
        self.tree.delete(*self.tree.get_children())
        self.tree.configure(show="headings" if mode == "all" else "tree headings")
        self._rows = {row["student_id"]: row for row in report["rows"]}
        groups = {}
        for index, row in enumerate(report["rows"]):
            parent = ""
            if mode != "all":
                group = (row["grade"] or "NOT GRADED") if mode == "grade" else row["outcome"]
                if group not in groups:
                    group_id = f"group:{group}"
                    self.tree.insert("", "end", iid=group_id, text=group, open=True, tags=("group",))
                    groups[group] = [group_id, 0]
                groups[group][1] += 1
                parent = groups[group][0]
            values = (row["student_id"], row["name"], row["email"], row["subjects"], "—" if row["average"] is None else f"{row['average']:.2f}", row["grade"] or "—", row["outcome"])
            self.tree.insert(parent, "end", iid=f"student:{row['student_id']}", values=values, tags=("even" if index % 2 == 0 else "odd",))
        for group, (group_id, count) in groups.items():
            self.tree.item(group_id, text=f"{group} ({count})")
        if report["rows"]:
            self.empty_label.place_forget()
        else:
            self.empty_label.configure(text="No matching students" if self.search_var.get().strip() else "No student records")
            self.empty_label.place(relx=0.5, rely=0.55, anchor="center")
        total = report["summary"]["students"]
        self.status_var.set(message or f"Showing {len(report['rows'])} of {total} students · {report['summary']['ungraded']} not graded")
        self.remove_button.configure(state="disabled")
        self.clear_button.configure(state="normal" if total else "disabled")
        return True

    def _selected_id(self):
        """Return a selected student ID, excluding nonrecord group headings."""
        selection = self.tree.selection()
        if selection and selection[0].startswith("student:"):
            return selection[0].split(":", 1)[1]
        return None

    def _selection_changed(self, event=None):
        """Enable removal only when a real student record has been selected."""
        self.remove_button.configure(state="normal" if self._selected_id() is not None else "disabled")

    def request_remove(self):
        """Open a cancellable confirmation for the selected student and enrolments."""
        student_id = self._selected_id()
        if student_id is None:
            self.application.display_error("Select a student record first.")
            return False
        row = self._rows[student_id]
        self.application.request_confirmation("Remove student?", f"{row['name']} ({student_id}) and their {row['subjects']} enrolments will be removed. This action cannot be undone in the app.", partial(self._remove_confirmed, student_id))
        return True

    def _remove_confirmed(self, student_id):
        """Remove only the approved record and refresh the dashboard after persistence."""
        try:
            self.application.admin_service.remove_student(student_id)
        except (ValueError, PermissionError, DatabaseError) as error:
            self.application.display_error(str(error))
            return False
        return self.refresh_students(message="Student removed successfully.")

    def request_clear(self):
        """Ask for the CLEAR phrase before deleting any account from the shared file."""
        self.application.request_confirmation("Clear all student records?", "Every student and their enrolments in this database will be removed. This action cannot be undone in the app.", self._clear_confirmed, phrase="CLEAR")
        return True

    def _clear_confirmed(self):
        """Clear through the authenticated service after the confirmation dialog succeeds."""
        try:
            self.application.admin_service.clear_students("CLEAR")
        except (ValueError, PermissionError, DatabaseError) as error:
            self.application.display_error(str(error))
            return False
        return self.refresh_students(message="All student records cleared.")
