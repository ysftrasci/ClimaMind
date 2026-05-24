"""Authentication and account management (no UI)."""

import random
import uuid
from collections.abc import Callable
from dataclasses import dataclass

from climamind.domain.models.user import User
from climamind.infrastructure.email.smtp_email_sender import EmailError, SmtpEmailSender
from climamind.infrastructure.persistence.user_repository import UserRepository
from climamind.services.exceptions import (
    AuthError,
    EmailNotVerifiedError,
    EmptyFieldsError,
    InvalidCredentialsError,
    InvalidResetCodeError,
    NotAuthenticatedError,
    PasswordMismatchError,
    PasswordTooShortError,
    UserAlreadyExistsError,
    UserNotFoundError,
    VerificationCodeError,
)
from climamind.services.session_manager import SessionManager


@dataclass
class PendingRegistration:
    code: str
    password: str


class VerificationCodeStore:
    """In-memory pending registration codes (``verification_codes`` in maincode.py)."""

    def __init__(self) -> None:
        self._codes: dict[str, PendingRegistration] = {}

    def put(self, email: str, code: str, password: str) -> None:
        self._codes[email.strip().lower()] = PendingRegistration(code=code, password=password)

    def pop(self, email: str) -> PendingRegistration | None:
        return self._codes.pop(email.strip().lower(), None)

    def get(self, email: str) -> PendingRegistration | None:
        return self._codes.get(email.strip().lower())

    def verify(self, email: str, entered_code: str) -> PendingRegistration:
        email = email.strip().lower()
        pending = self.get(email)
        if not pending or pending.code != entered_code.strip():
            raise VerificationCodeError("Incorrect or expired verification code!")
        return pending


class AuthService:
    """Login, registration, password reset, and account deletion."""

    MIN_PASSWORD_LENGTH = 6

    def __init__(
        self,
        user_repository: UserRepository,
        session_manager: SessionManager,
        email_sender: SmtpEmailSender | None = None,
        verification_store: VerificationCodeStore | None = None,
        on_account_deleted: Callable[[str], None] | None = None,
    ) -> None:
        self._user_repository = user_repository
        self._session = session_manager
        self._email_sender = email_sender or SmtpEmailSender()
        self._verification_store = verification_store or VerificationCodeStore()
        self._on_account_deleted = on_account_deleted

    @property
    def session(self) -> SessionManager:
        return self._session

    def login(self, email: str, password: str) -> str:
        """
        Authenticate and start a session.

        Returns:
            Welcome message suffix (email local-part).

        Raises:
            InvalidCredentialsError, EmailNotVerifiedError
        """
        email = email.strip().lower()
        users = self._user_repository.load_all()
        user = users.get(email)

        if not user or user.password != password:
            raise InvalidCredentialsError("Incorrect email or password.")

        if not user.verified:
            raise EmailNotVerifiedError(
                "Your email address is not verified yet. "
                "Please check your email or register again."
            )

        self._session.set_email(email)
        return email.split("@")[0]

    def logout(self) -> None:
        self._session.clear()

    def register(
        self, email: str, password: str, confirm_password: str
    ) -> str:
        """
        Validate registration, send verification email, store pending code.

        Returns:
            Normalized email (UI navigates to verification screen).

        Raises:
            EmptyFieldsError, PasswordMismatchError, UserAlreadyExistsError, EmailError
        """
        email = email.strip().lower()
        if not email or not password or not confirm_password:
            raise EmptyFieldsError("Please fill in all fields.")
        if password != confirm_password:
            raise PasswordMismatchError("Passwords do not match!")

        users = self._user_repository.load_all()
        if email in users:
            raise UserAlreadyExistsError("This email is already registered!")

        code = str(random.randint(100000, 999999))
        self._verification_store.put(email, code, password)
        self._email_sender.send(
            email,
            "Clima Mind Verification Code",
            (
                f"Your verification code is: {code}\n\n"
                f"Please enter this code to complete your registration.\n\n"
                f"-- Clima Mind --"
            ),
        )
        return email

    def verify_registration(self, email: str, entered_code: str) -> None:
        """
        Complete registration after email verification.

        Raises:
            VerificationCodeError
        """
        email = email.strip().lower()
        pending = self._verification_store.verify(email, entered_code)
        self._verification_store.pop(email)

        users = self._user_repository.load_all()
        users[email] = User(
            password=pending.password,
            verified=True,
        )
        if not self._user_repository.save_all(users):
            raise AuthError("Could not save user data.")

    def request_password_reset(self, email: str) -> str:
        """
        Generate reset code, persist on user, send email.

        Returns:
            Normalized email (UI navigates to reset screen).

        Raises:
            EmptyFieldsError, UserNotFoundError, EmailError
        """
        email = email.strip().lower()
        if not email:
            raise EmptyFieldsError("Please enter your email address!")

        users = self._user_repository.load_all()
        if email not in users:
            raise UserNotFoundError("This email address is not registered!")

        reset_code = str(uuid.uuid4())[:8]
        users[email].reset_code = reset_code
        if not self._user_repository.save_all(users):
            raise AuthError("Could not save user data.")

        self._email_sender.send(
            email,
            "Clima Mind Password Reset Request",
            (
                f"Hello,\n\nYour password reset request has been received. "
                f"Your reset code is: {reset_code}\n"
                f"Use this code to reset your password.\n\n"
                f"Have a great day!\nClima Mind Team"
            ),
        )
        return email

    def reset_password(
        self,
        email: str,
        reset_code: str,
        new_password: str,
        confirm_password: str,
    ) -> None:
        """
        Apply a new password using the emailed reset code.

        Raises:
            EmptyFieldsError, InvalidResetCodeError, PasswordMismatchError
        """
        email = email.strip().lower()
        if not reset_code or not new_password or not confirm_password:
            raise EmptyFieldsError("Please fill in all fields!")
        if new_password != confirm_password:
            raise PasswordMismatchError("Passwords do not match!")

        users = self._user_repository.load_all()
        user = users.get(email)
        if not user or user.reset_code != reset_code.strip():
            raise InvalidResetCodeError("Invalid reset code!")

        user.password = new_password
        user.reset_code = None
        if not self._user_repository.save_all(users):
            raise AuthError("Could not save user data.")

    def change_password(
        self,
        email: str,
        current_password: str,
        new_password: str,
        confirm_password: str,
    ) -> None:
        """
        Change password for a logged-in user.

        Raises:
            NotAuthenticatedError, EmptyFieldsError, PasswordMismatchError,
            InvalidCredentialsError, PasswordTooShortError
        """
        if not email:
            raise NotAuthenticatedError(
                "You must be logged in to change your password."
            )
        email = email.strip().lower()
        if not current_password or not new_password or not confirm_password:
            raise EmptyFieldsError("All fields are required!")
        if new_password != confirm_password:
            raise PasswordMismatchError(
                "New password and confirmation do not match!"
            )
        if len(new_password) < self.MIN_PASSWORD_LENGTH:
            raise PasswordTooShortError(
                "New password must be at least 6 characters long!"
            )

        users = self._user_repository.load_all()
        user = users.get(email)
        if not user or user.password != current_password:
            raise InvalidCredentialsError("Current password is incorrect!")

        user.password = new_password
        if not self._user_repository.save_all(users):
            raise AuthError("Could not save user data.")

    def delete_account(self, email: str) -> None:
        """
        Permanently remove a user account.

        Raises:
            UserNotFoundError
        """
        email = email.strip().lower()
        users = self._user_repository.load_all()
        if email not in users:
            raise UserNotFoundError("Account not found or an error occurred.")

        del users[email]
        if not self._user_repository.save_all(users):
            raise AuthError("Could not save user data.")

        if self._session.email == email:
            self._session.clear()

        if self._on_account_deleted:
            self._on_account_deleted(email)

    def get_user(self, email: str) -> User | None:
        return self._user_repository.load_all().get(email.strip().lower())
