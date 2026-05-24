"""Application dependency container (shared by app and views)."""

from __future__ import annotations

from dataclasses import dataclass

import tkinter as tk

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


@dataclass
class AppContext:
    """Container for all wired application dependencies (DI root)."""

    root: tk.Tk
    theme: UiTheme
    navigation: NavigationController
    image_registry: ImageRegistry

    sfx_player: SfxPlayer
    music_player: MusicPlayer

    user_repository: UserRepository
    weather_client: OpenWeatherClient
    email_sender: SmtpEmailSender
    reminder_scheduler: ReminderScheduler

    session_manager: SessionManager
    verification_store: VerificationCodeStore
    weather_advisor: WeatherAdvisor
    query_parser: QueryParser
    social_share_service: SocialShareService

    scheduled_weather_reporter: ScheduledWeatherReporter
    auth_service: AuthService
    account_service: AccountService
    favorites_service: FavoritesService
    joyuci_service: JoyuciService
    reminder_service: ReminderService
