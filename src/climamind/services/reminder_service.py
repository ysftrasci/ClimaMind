"""Reminder settings persistence and scheduler coordination."""

import re
from collections.abc import Callable

from climamind.config.settings import DAY_MAP_EN_TO_SCHEDULE, DAYS_OF_WEEK_EN
from climamind.domain.models.reminder import ReminderSettings
from climamind.domain.models.user import User
from climamind.infrastructure.persistence.user_repository import UserRepository
from climamind.infrastructure.scheduling.reminder_scheduler import (
    ReminderScheduler,
    ReminderSchedulingError,
)

_TIME_PATTERN = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")
_VALID_FREQUENCIES = frozenset({"every_day", "weekdays", "weekends", "custom"})


class ReminderValidationError(Exception):
    """Raised when reminder input fails validation."""


class ReminderService:
    """
    Business logic for user weather reminders (no UI).

    Extracted from the ``reminder()`` screen in maincode.py.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        reminder_scheduler: ReminderScheduler,
        report_callback: Callable[[str, str], None],
    ) -> None:
        self._user_repository = user_repository
        self._scheduler = reminder_scheduler
        self._report_callback = report_callback

    @staticmethod
    def validate_time_format(time_str: str) -> None:
        if not _TIME_PATTERN.match(time_str.strip()):
            raise ReminderValidationError(
                "Time must be in HH:MM format (24-hour)!"
            )

    @staticmethod
    def validate_required_fields(time_str: str, city: str) -> None:
        if not time_str or not str(time_str).strip() or not city or not str(city).strip():
            raise ReminderValidationError("Time and city are required!")

    @classmethod
    def build_settings(
        cls,
        time_str: str,
        city: str,
        frequency: str,
        custom_days: list[str] | None = None,
    ) -> ReminderSettings:
        """
        Validate inputs and build a ``ReminderSettings`` instance.

        Raises:
            ReminderValidationError: On invalid or missing input.
        """
        time_str = time_str.strip()
        city = city.strip()
        cls.validate_required_fields(time_str, city)
        cls.validate_time_format(time_str)

        if frequency not in _VALID_FREQUENCIES:
            raise ReminderValidationError(f"Unknown frequency: {frequency}")

        days = list(custom_days or [])
        if frequency == "custom":
            invalid = [d for d in days if d not in DAY_MAP_EN_TO_SCHEDULE]
            if invalid:
                raise ReminderValidationError(
                    f"Invalid custom days: {', '.join(invalid)}. "
                    f"Use: {', '.join(DAYS_OF_WEEK_EN)}"
                )

        return ReminderSettings(
            time=time_str,
            city=city,
            frequency=frequency,
            custom_days=days if frequency == "custom" else [],
        )

    def get_reminder_settings(self, email: str) -> ReminderSettings:
        users = self._user_repository.load_all()
        user = users.get(email)
        if not user:
            return ReminderSettings()
        return user.reminder

    def save_reminder(self, email: str, settings: ReminderSettings) -> None:
        """
        Persist reminder settings and register scheduler jobs.

        Raises:
            ReminderValidationError: If settings are incomplete.
            ReminderSchedulingError: If the scheduler rejects the job.
        """
        if not settings.is_complete():
            raise ReminderValidationError("Time, city, and frequency are required.")

        users = self._user_repository.load_all()
        if email not in users:
            raise ReminderValidationError(f"User not found: {email}")

        job = lambda e=email, c=settings.city: self._report_callback(e, c)
        self._scheduler.register_reminder(email, settings, job)

        users[email].reminder = settings
        if not self._user_repository.save_all(users):
            raise ReminderSchedulingError("Could not save reminder settings.")

    def save_reminder_from_form(
        self,
        email: str,
        time_str: str,
        city: str,
        frequency: str,
        custom_days: list[str] | None = None,
    ) -> ReminderSettings:
        """Validate form values, then persist and schedule."""
        settings = self.build_settings(time_str, city, frequency, custom_days)
        self.save_reminder(email, settings)
        return settings

    def clear_reminder(self, email: str) -> None:
        """Remove scheduler jobs and clear stored reminder settings for *email*."""
        self._scheduler.clear_reminders_for_user(email)
        users = self._user_repository.load_all()
        if email in users:
            users[email].reminder = ReminderSettings()
            self._user_repository.save_all(users)

    def reload_all_reminders(self, users: dict[str, User] | None = None) -> int:
        """Reload every user's reminder from disk into the scheduler."""
        if users is None:
            users = self._user_repository.load_all()
        return self._scheduler.load_from_users(users, self._report_callback)
