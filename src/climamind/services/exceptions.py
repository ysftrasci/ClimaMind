"""Shared service-layer exceptions."""


class AuthError(Exception):
    """Base class for authentication failures."""


class EmptyFieldsError(AuthError):
    """Required form fields are missing."""


class PasswordMismatchError(AuthError):
    """Password and confirmation do not match."""


class InvalidCredentialsError(AuthError):
    """Email/password combination is wrong."""


class EmailNotVerifiedError(AuthError):
    """Account exists but email is not verified."""


class UserAlreadyExistsError(AuthError):
    """Email is already registered."""


class UserNotFoundError(AuthError):
    """No account for the given email."""


class VerificationCodeError(AuthError):
    """Registration verification code is invalid or expired."""


class InvalidResetCodeError(AuthError):
    """Password reset code does not match."""


class NotAuthenticatedError(AuthError):
    """Action requires a logged-in user."""


class PasswordTooShortError(AuthError):
    """Password does not meet minimum length."""


class EmptyQueryError(Exception):
    """Joyuci query text is empty."""
