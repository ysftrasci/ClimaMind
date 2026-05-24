"""Background scheduling of weather reminder jobs via the ``schedule`` library."""

import time
import traceback
from collections.abc import Callable
from threading import Thread

import schedule

from climamind.config.settings import DAY_MAP_EN_TO_SCHEDULE
from climamind.domain.models.reminder import ReminderSettings
from climamind.domain.models.user import User


class ReminderSchedulingError(Exception):
    """Raised when a reminder cannot be registered with the scheduler."""


class ReminderScheduler:
    """
    Manages ``schedule`` jobs for per-user weather email reminders.

    Mirrors ``run_schedule`` and ``load_and_schedule_reminders`` from maincode.py.
    """

    WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday"]
    WEEKENDS = ["saturday", "sunday"]

    def __init__(self) -> None:
        self._thread_started = False

    @staticmethod
    def user_tag(email: str) -> str:
        return f"reminder_{email}"

    def start_daemon_thread(self) -> None:
        """Start the background loop that runs ``schedule.run_pending()``."""
        if self._thread_started:
            return
        thread = Thread(target=self._run_loop, daemon=True)
        thread.start()
        self._thread_started = True

    def clear_all(self) -> None:
        """Remove every scheduled job."""
        schedule.clear()

    def clear_reminders_for_user(self, email: str) -> None:
        """Remove scheduled jobs tagged for *email*."""
        schedule.clear(self.user_tag(email))

    def register_reminder(
        self,
        email: str,
        settings: ReminderSettings,
        job: Callable[[], None],
    ) -> None:
        """
        Clear existing jobs for *email* and queue new ones from *settings*.

        Raises:
            ReminderSchedulingError: If frequency is unknown or scheduling fails.
        """
        if not settings.is_complete():
            raise ReminderSchedulingError(
                f"Incomplete reminder settings for {email}."
            )

        tag = self.user_tag(email)
        schedule.clear(tag)
        time_str = settings.time
        frequency = settings.frequency
        custom_days = settings.custom_days

        try:
            if frequency == "every_day":
                schedule.every().day.at(time_str).do(job).tag(tag)
            elif frequency == "weekdays":
                for day in self.WEEKDAYS:
                    getattr(schedule.every(), day).at(time_str).do(job).tag(tag)
            elif frequency == "weekends":
                for day in self.WEEKENDS:
                    getattr(schedule.every(), day).at(time_str).do(job).tag(tag)
            elif frequency == "custom" and custom_days:
                for day_en in custom_days:
                    schedule_day = DAY_MAP_EN_TO_SCHEDULE.get(day_en)
                    if schedule_day:
                        getattr(schedule.every(), schedule_day).at(time_str).do(
                            job
                        ).tag(tag)
            elif frequency == "custom":
                pass
            else:
                raise ReminderSchedulingError(
                    f"Unknown reminder frequency for {email}: {frequency}"
                )

            print(
                f"[OK] Reminder scheduled for {email}: {settings.city} "
                f"@ {time_str} - {frequency}"
            )
        except ReminderSchedulingError:
            raise
        except Exception as exc:
            raise ReminderSchedulingError(
                f"Could not schedule reminder for {email}: {exc}"
            ) from exc

    def load_from_users(
        self,
        users: dict[str, User],
        report_callback: Callable[[str, str], None],
    ) -> int:
        """
        Reload all reminders from persisted user data.

        Args:
            users: All users keyed by email.
            report_callback: ``(email, city) -> None`` invoked by each job.

        Returns:
            Number of users whose reminders were scheduled successfully.
        """
        print("Loading and scheduling existing reminders...")
        self.clear_all()
        loaded_count = 0

        for email, user in users.items():
            settings = user.reminder
            if not settings.time and not settings.city and not settings.frequency:
                continue

            if not settings.is_complete():
                print(f"[WARN] Incomplete reminder data for {email}, skipping.")
                continue

            job = lambda e=email, c=settings.city: report_callback(e, c)
            try:
                if settings.frequency == "custom":
                    valid_days = [
                        d
                        for d in settings.custom_days
                        if d in DAY_MAP_EN_TO_SCHEDULE
                    ]
                    if not valid_days:
                        print(
                            f"[WARN] No valid English days found for custom "
                            f"reminder ({email}), skipping."
                        )
                        continue
                    temp = ReminderSettings(
                        time=settings.time,
                        city=settings.city,
                        frequency=settings.frequency,
                        custom_days=valid_days,
                    )
                    self.register_reminder(email, temp, job)
                else:
                    self.register_reminder(email, settings, job)
                loaded_count += 1
            except ReminderSchedulingError as exc:
                print(f"[ERROR] Error scheduling reminder for {email}: {exc}")
            except Exception as exc:
                print(
                    f"[ERROR] Error scheduling reminder for {email}: {exc}\n"
                    f"{traceback.format_exc()}"
                )

        print(f"--- {loaded_count} reminder(s) loaded and scheduled ---")
        return loaded_count

    @staticmethod
    def _run_loop() -> None:
        print("Scheduler thread started.")
        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as exc:
                print(f"[ERROR] Error in scheduler thread: {exc}")
                time.sleep(10)
