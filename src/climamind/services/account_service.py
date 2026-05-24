"""Account profile updates."""

from climamind.domain.models.user import User
from climamind.infrastructure.persistence.user_repository import UserRepository


class AccountError(Exception):
    """Base class for account profile errors."""


class NotAuthenticatedError(AccountError):
    """User must be logged in."""


class AccountService:
    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository = user_repository

    def get_profile(self, email: str) -> User:
        return self._get_user(email)

    def update_profile(
        self,
        email: str,
        *,
        username: str | None = None,
        district: str | None = None,
        profile_picture: str | None = None,
    ) -> bool:
        """
        Update account fields. Returns True if anything changed and was saved.
        """
        user = self._get_user(email)
        changed = False
        if username is not None and username != user.account.username:
            user.account.username = username.strip()
            changed = True
        if district is not None and district != user.account.district:
            user.account.district = district.strip().title()
            changed = True
        if (
            profile_picture is not None
            and profile_picture != user.account.profile_picture
            and profile_picture != "No file selected"
        ):
            user.account.profile_picture = profile_picture
            changed = True
        if changed:
            users = self._user_repository.load_all()
            users[email.strip().lower()] = user
            if not self._user_repository.save_all(users):
                raise AccountError("Could not save account information.")
        return changed

    def _get_user(self, email: str) -> User:
        if not email:
            raise NotAuthenticatedError("You must be logged in.")
        email = email.strip().lower()
        users = self._user_repository.load_all()
        if email not in users:
            raise NotAuthenticatedError("User not found.")
        return users[email]
