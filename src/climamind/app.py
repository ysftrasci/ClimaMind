"""
Clima Mind application bootstrap and dependency wiring.

From the project root (``UmbrellaReminder/``)::

    python run.py
"""

from __future__ import annotations

import tkinter as tk

from climamind.config.paths import ensure_music_folder
from climamind.context import AppContext
from climamind.infrastructure.api.openweather_client import OpenWeatherClient
from climamind.infrastructure.audio.music_player import MusicPlayer
from climamind.infrastructure.audio.sfx_player import SfxPlayer
from climamind.infrastructure.email.smtp_email_sender import SmtpEmailSender
from climamind.infrastructure.persistence.user_repository import UserRepository
from climamind.infrastructure.scheduling.reminder_scheduler import ReminderScheduler
from climamind.services.account_service import AccountService
from climamind.services.auth_service import AuthService, VerificationCodeStore
from climamind.services.favorites_service import FavoritesService
from climamind.services.joyuci_service import JoyuciService
from climamind.services.query_parser import QueryParser
from climamind.services.reminder_service import ReminderService
from climamind.services.scheduled_weather_reporter import ScheduledWeatherReporter
from climamind.services.session_manager import SessionManager
from climamind.services.social_share_service import SocialShareService
from climamind.services.weather_advisor import WeatherAdvisor
from climamind.ui.assets.image_registry import ImageRegistry
from climamind.ui.navigation import NavigationController
from climamind.ui.theme import UiTheme
from climamind.ui.views.main_menu_view import MainMenuView


class ClimaMindApp:
    """Initializes services and runs the Tkinter main loop."""

    WINDOW_TITLE = "Clima Mind - Weather & Reminders"

    def __init__(self) -> None:
        ensure_music_folder()
        self.root = tk.Tk()
        self.root.title(self.WINDOW_TITLE)
        self.root.configure(bg=UiTheme().default_window_bg)
        self.ctx: AppContext | None = None

    def _wire_dependencies(self) -> AppContext:
        theme = UiTheme()
        navigation = NavigationController(self.root, theme)
        image_registry = ImageRegistry(master=self.root)
        image_registry.load_all(self.root)

        sfx_player = SfxPlayer()
        music_player = MusicPlayer.create(sfx_player)

        user_repository = UserRepository()
        weather_client = OpenWeatherClient()
        email_sender = SmtpEmailSender()
        reminder_scheduler = ReminderScheduler()

        session_manager = SessionManager()
        verification_store = VerificationCodeStore()
        weather_advisor = WeatherAdvisor()
        query_parser = QueryParser()
        social_share_service = SocialShareService()

        scheduled_weather_reporter = ScheduledWeatherReporter(
            weather_client=weather_client,
            email_sender=email_sender,
        )

        auth_service = AuthService(
            user_repository=user_repository,
            session_manager=session_manager,
            email_sender=email_sender,
            verification_store=verification_store,
            on_account_deleted=reminder_scheduler.clear_reminders_for_user,
        )

        joyuci_service = JoyuciService(
            user_repository=user_repository,
            query_parser=query_parser,
            weather_client=weather_client,
        )

        reminder_service = ReminderService(
            user_repository=user_repository,
            reminder_scheduler=reminder_scheduler,
            report_callback=scheduled_weather_reporter.send_report,
        )

        account_service = AccountService(user_repository=user_repository)
        favorites_service = FavoritesService(
            user_repository=user_repository,
            weather_client=weather_client,
        )

        return AppContext(
            root=self.root,
            theme=theme,
            navigation=navigation,
            image_registry=image_registry,
            sfx_player=sfx_player,
            music_player=music_player,
            user_repository=user_repository,
            weather_client=weather_client,
            email_sender=email_sender,
            reminder_scheduler=reminder_scheduler,
            session_manager=session_manager,
            verification_store=verification_store,
            weather_advisor=weather_advisor,
            query_parser=query_parser,
            social_share_service=social_share_service,
            scheduled_weather_reporter=scheduled_weather_reporter,
            auth_service=auth_service,
            account_service=account_service,
            favorites_service=favorites_service,
            joyuci_service=joyuci_service,
            reminder_service=reminder_service,
        )

    def _setup_window(self) -> None:
        self.root.attributes("-fullscreen", True)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self) -> None:
        if self.ctx and self.ctx.music_player.current_track:
            self.ctx.music_player.stop()
        print("👋 Closing application...")
        self.root.destroy()

    def _start_background_services(self) -> None:
        assert self.ctx is not None
        self.ctx.reminder_scheduler.start_daemon_thread()
        self.ctx.reminder_service.reload_all_reminders()

    def run(self) -> None:
        """Build the dependency graph, show the shell window, and enter mainloop."""
        self.ctx = self._wire_dependencies()
        self._setup_window()
        self._start_background_services()
        MainMenuView(self.ctx).show()
        self.root.mainloop()


def main() -> None:
    ClimaMindApp().run()


if __name__ == "__main__":
    main()
