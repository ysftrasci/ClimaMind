"""Weather search screen."""

from __future__ import annotations

import webbrowser

import tkinter as tk
from tkinter import messagebox

from climamind.context import AppContext
from climamind.domain.models.weather import CurrentWeather
from climamind.infrastructure.api.openweather_client import WeatherError
from climamind.infrastructure.email.smtp_email_sender import EmailError
from climamind.services.favorites_service import (
    CityAlreadyFavoriteError,
    FavoritesError,
    InvalidCityError,
    NotAuthenticatedError,
)
from climamind.services.weather_advisor import WeatherAdvisor
from climamind.ui.views.helpers import (
    create_welcome_frame,
    entry_style_copy,
    panel_bg,
)
from climamind.ui.views.main_menu_view import MainMenuView
from climamind.ui.views.share_helper import execute_share
from climamind.ui.widgets.back_button import BackButtonPlacement, create_back_button
from climamind.ui.widgets.cloud_animation import CloudAnimation
from climamind.ui.widgets.weather_animations import WeatherAnimation


class SearchWeatherView:
    def __init__(self, ctx: AppContext) -> None:
        self._ctx = ctx
        self._cloud_anim: CloudAnimation | None = None
        self._weather_anim: WeatherAnimation | None = None
        self._current_weather: CurrentWeather | None = None
        self._current_city: str = ""

    def show(self) -> None:
        if self._ctx.music_player.current_track:
            self._ctx.music_player.stop()
        self._ctx.music_player.page_active = False
        self._ctx.navigation.navigate(
            self._build,
            view_name="search_weather",
            bg_color=self._ctx.theme.default_window_bg,
            on_leave=self._cleanup,
        )

    def _cleanup(self) -> None:
        if self._cloud_anim is not None:
            self._cloud_anim.stop()
            self._cloud_anim = None
        if self._weather_anim is not None:
            self._weather_anim.stop()
            self._weather_anim = None

    def _build(self) -> None:
        ctx = self._ctx
        theme = ctx.theme
        root = ctx.root
        panel = panel_bg(theme)
        bg = theme.default_window_bg

        outer = tk.Frame(root, bg=bg)
        outer.pack(fill="both", expand=True, padx=20, pady=20)

        canvas = tk.Canvas(outer, bg=bg, highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        from climamind.ui.widgets.cloud_animation import CloudAnimationConfig, start_cloud_animation

        self._cloud_anim = start_cloud_animation(
            canvas,
            root,
            ctx.image_registry.get("clouds"),
            config=CloudAnimationConfig(count=8, y_max_ratio=0.7),
        )

        create_welcome_frame(
            canvas,
            "Search Weather",
            "Enter a city name to see current conditions.",
            theme,
        ).place(relx=0.5, rely=0.08, anchor="n")

        search_panel = tk.Frame(canvas, bg=panel, bd=2, relief=tk.GROOVE, padx=20, pady=20)
        search_panel.place(relx=0.5, rely=0.32, anchor="center")

        tk.Label(
            search_panel,
            text="Enter city name:",
            font=theme.font(theme.large_font_size),
            bg=panel,
        ).pack(anchor="w")
        city_entry = tk.Entry(
            search_panel, **entry_style_copy(theme), width=40
        )
        city_entry.pack(pady=8)
        city_entry.focus()

        favorites_frame = tk.Frame(search_panel, bg=panel)
        favorites_frame.pack(pady=5, fill="x")

        result_panel = tk.Frame(canvas, bg=panel, bd=2, relief=tk.GROOVE, padx=15, pady=15)
        result_panel.place(relx=0.5, rely=0.68, anchor="center", width=700, height=280)

        result_inner = tk.Frame(result_panel, bg=panel)
        result_inner.pack(fill="both", expand=True)
        anim_holder = tk.Frame(result_inner, bg=panel)
        anim_holder.pack(fill="x")
        self._weather_anim = WeatherAnimation(anim_holder, theme=theme)
        content_frame = tk.Frame(result_inner, bg=panel)
        content_frame.pack(fill="both", expand=True, pady=5)

        def refresh_favorites() -> None:
            for w in favorites_frame.winfo_children():
                w.destroy()
            email = ctx.session_manager.email
            if not email:
                return
            try:
                cities = ctx.favorites_service.list_favorites(email)
            except NotAuthenticatedError:
                return
            if not cities:
                tk.Label(
                    favorites_frame,
                    text="No favorites added yet.",
                    font=theme.font(theme.large_font_size, italic=True),
                    bg=panel,
                ).pack(pady=5)
                return
            tk.Label(
                favorites_frame,
                text="Select from favorites:",
                font=theme.font(theme.large_font_size),
                bg=panel,
            ).pack(anchor="w")
            row = tk.Frame(favorites_frame, bg=panel)
            row.pack()
            for city in cities[:6]:
                tk.Button(
                    row,
                    text=city,
                    width=18,
                    font=theme.font(theme.base_font_size),
                    bg="#2196F3",
                    fg=theme.colors.white,
                    command=lambda c=city: _search_city(c),
                ).pack(side=tk.LEFT, padx=4, pady=4)

        def _clear_result() -> None:
            for w in content_frame.winfo_children():
                w.destroy()
            if self._weather_anim:
                self._weather_anim.stop()

        def _show_weather(city: str, weather: CurrentWeather) -> None:
            self._current_city = city
            self._current_weather = weather
            _clear_result()
            desc = weather.description.capitalize()
            tk.Label(
                content_frame,
                text=f"{city}: {desc}, {weather.temp:.1f}°C",
                font=theme.font(theme.large_font_size),
                bg=panel,
            ).pack(pady=5)

            icon_map = {
                "rain": "umbrella",
                "snow": "snowy",
                "clear": "contrast",
                "mist": "fog",
                "fog": "fog",
            }
            icon_key = icon_map.get(weather.main.lower(), "clouds")
            icon = ctx.image_registry.get(icon_key)
            if icon:
                tk.Label(content_frame, image=icon, bg=panel).pack(pady=5)

            if self._weather_anim:
                self._weather_anim.start(weather)

            share_row = tk.Frame(content_frame, bg=panel)
            share_row.pack(pady=8)
            for text, color, platform in [
                ("Instagram", "#E1306C", "instagram"),
                ("WhatsApp", "#25D366", "whatsapp"),
                ("LinkedIn", "#0077B5", "linkedin"),
                ("X", "#000000", "x"),
            ]:
                tk.Button(
                    share_row,
                    text=text,
                    width=14,
                    bg=color,
                    fg=theme.colors.white,
                    font=theme.font(theme.base_font_size, bold=True),
                    command=lambda p=platform: [
                        ctx.sfx_player.play_click(),
                        execute_share(
                            ctx,
                            city,
                            p,
                            weather=weather,
                        ),
                    ],
                ).pack(side=tk.LEFT, padx=4)

            email = ctx.session_manager.email
            if email:
                def add_favorite() -> None:
                    ctx.sfx_player.play_click()
                    try:
                        ctx.favorites_service.add_favorite(email, city)
                        messagebox.showinfo("Success", f"{city} added to favorites!")
                        refresh_favorites()
                    except CityAlreadyFavoriteError as exc:
                        messagebox.showinfo("Info", str(exc))
                    except (InvalidCityError, FavoritesError) as exc:
                        messagebox.showerror("Error", str(exc))

                tk.Button(
                    content_frame,
                    text="Add to Favorites",
                    bg="#2196F3",
                    fg=theme.colors.white,
                    font=theme.font(theme.base_font_size, bold=True),
                    command=add_favorite,
                ).pack(pady=5)

            if weather.lat is not None and weather.lon is not None:
                tk.Button(
                    content_frame,
                    text="View on Map",
                    width=15,
                    bg="#FF9800",
                    fg=theme.colors.white,
                    font=theme.font(theme.base_font_size, bold=True),
                    command=lambda: webbrowser.open(
                        f"https://www.openstreetmap.org/?mlat={weather.lat}"
                        f"&mlon={weather.lon}#map=12/{weather.lat}/{weather.lon}"
                    ),
                ).pack(pady=5)

        def _send_email(city: str, weather: CurrentWeather) -> None:
            email = ctx.session_manager.email
            if not email:
                return
            advice = WeatherAdvisor.get_advice(weather.main)
            body = (
                f"Hello,\n\n📍 Weather for {city}:\n"
                f"🌡️ Temperature: {weather.temp:.1f}°C\n"
                f"🌤️ Condition: {weather.description.capitalize()}\n\n"
                f"💡 {advice}\n\nBest regards,\n-- Clima Mind --"
            )
            try:
                ctx.email_sender.send(
                    email,
                    f"Weather Update for {city}",
                    body,
                )
                messagebox.showinfo(
                    "Email Sent",
                    f"Weather update for {city} has been sent to your email!",
                )
            except EmailError as exc:
                messagebox.showerror("Email Error", str(exc))

        def _search_city(city: str | None = None) -> None:
            ctx.sfx_player.play_click()
            name = (city or city_entry.get()).strip()
            if not name:
                messagebox.showwarning("Input Error", "Please enter a city name.")
                return
            try:
                weather = ctx.weather_client.fetch_current(name)
            except WeatherError:
                _clear_result()
                tk.Label(
                    content_frame,
                    text=f"Could not find weather data for '{name}'.",
                    font=theme.font(theme.large_font_size, italic=True),
                    bg=panel,
                    fg="red",
                ).pack(pady=10)
                return
            _show_weather(name.title(), weather)
            _send_email(name.title(), weather)

        tk.Button(
            search_panel,
            text="Search",
            bg=theme.colors.btn_green,
            fg=theme.colors.white,
            font=theme.font(theme.large_font_size, bold=True),
            width=20,
            command=lambda: _search_city(),
        ).pack(pady=10)
        city_entry.bind("<Return>", lambda _e: _search_city())

        refresh_favorites()

        create_back_button(
            outer,
            lambda: MainMenuView(ctx).show(),
            theme=theme,
            images=ctx.image_registry,
            sfx_player=ctx.sfx_player,
            placement=BackButtonPlacement.BOTTOM_CENTER,
        )
