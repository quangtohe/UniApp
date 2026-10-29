"""Shared validation rules for registration, CLI login and GUI login."""

import re


class Validator:
    """Validate credentials using the patterns inherited from the group's code."""

    EMAIL_PATTERN = r"[A-Za-z0-9._%+-]+@university\.com"
    PASSWORD_PATTERN = r"[A-Z][A-Za-z]{4,}[0-9]{3,}"
    PASSWORD_HELP = "Start with an uppercase letter, use at least 5 letters, then at least 3 digits."

    @staticmethod
    def validate_email(email):
        """Accept a nonempty university.com address matching the original rule."""
        return isinstance(email, str) and re.fullmatch(Validator.EMAIL_PATTERN, email) is not None

    @staticmethod
    def validate_password(password):
        """Require an uppercase initial, five or more letters, then three or more digits."""
        return isinstance(password, str) and re.fullmatch(Validator.PASSWORD_PATTERN, password) is not None

    @staticmethod
    def validate_login_fields(email, password):
        """Reject empty or incorrectly formatted credentials before authentication."""
        return Validator.validate_email(email) and Validator.validate_password(password)

    @staticmethod
    def require_credentials(email, password):
        """Raise a readable validation error without changing the supplied password."""
        if not email or not password:
            raise ValueError("Email and password are required.")
        if not Validator.validate_email(email):
            raise ValueError("Use an email address ending in @university.com.")
        if not Validator.validate_password(password):
            raise ValueError(Validator.PASSWORD_HELP)
