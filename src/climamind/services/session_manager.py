"""In-memory session state for the logged-in user."""


class SessionManager:
    """Replaces the global ``current_user = {'email': None}`` dict from maincode.py."""

    def __init__(self) -> None:
        self._email: str | None = None

    @property
    def email(self) -> str | None:
        return self._email

    def is_authenticated(self) -> bool:
        return self._email is not None

    def set_email(self, email: str) -> None:
        self._email = email.strip().lower()

    def clear(self) -> None:
        self._email = None

    def display_name(self) -> str:
        """Local-part of email or empty string when logged out."""
        if not self._email:
            return ""
        return self._email.split("@")[0]
