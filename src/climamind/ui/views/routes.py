"""Register all application view routes on the shared ViewRouter."""

from __future__ import annotations

from climamind.context import AppContext
from climamind.ui.views.account_settings_view import AccountSettingsView
from climamind.ui.views.change_password_view import ResetPasswordView
from climamind.ui.views.favorites_view import FavoritesView
from climamind.ui.views.joyuci_view import JoyuciView
from climamind.ui.views.login_view import LoginView
from climamind.ui.views.main_menu_view import MainMenuView
from climamind.ui.views.music_view import MusicView
from climamind.ui.views.register_view import RegisterView
from climamind.ui.views.reminder_view import ReminderView
from climamind.ui.views.search_weather_view import SearchWeatherView
from climamind.ui.views.settings_change_password_view import SettingsChangePasswordView
from climamind.ui.views.settings_view import SettingsView
from climamind.ui.views.view_router import ViewRouter


def build_view_router(ctx: AppContext) -> ViewRouter:
    router = ViewRouter(ctx)
    router.register("main_menu", lambda: MainMenuView(ctx).show())
    router.register("login", lambda: LoginView(ctx).show())
    router.register("register", lambda: RegisterView(ctx).show())
    router.register("search_weather", lambda: SearchWeatherView(ctx).show())
    router.register("joyuci", lambda: JoyuciView(ctx).show())
    router.register("reminder", lambda: ReminderView(ctx).show())
    router.register("music", lambda: MusicView(ctx).show())
    router.register("settings", lambda: SettingsView(ctx).show())
    router.register("account_settings", lambda: AccountSettingsView(ctx).show())
    router.register("favorites", lambda: FavoritesView(ctx).show())
    router.register(
        "change_password",
        lambda: SettingsChangePasswordView(ctx).show(),
    )
    return router
