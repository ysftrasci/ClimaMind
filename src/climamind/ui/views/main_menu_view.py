"""Main menu (logged-in and logged-out states)."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from PIL import Image, ImageTk

from climamind.context import AppContext
from climamind.infrastructure.api.openweather_client import WeatherError
from climamind.ui.views.helpers import create_welcome_frame
from climamind.ui.views.view_router import ViewRouter
from climamind.ui.widgets.cloud_animation import CloudAnimation, CloudAnimationConfig, start_cloud_animation


class MainMenuView:
    def __init__(self, ctx: AppContext) -> None:
        self._ctx = ctx
        from climamind.ui.views.routes import build_view_router

        self._router: ViewRouter = build_view_router(ctx)
        self._cloud_anim: CloudAnimation | None = None

    def show(self) -> None:
        self._ctx.root.attributes("-fullscreen", True)
        self._ctx.navigation.navigate(
            self._build,
            view_name="main_menu",
            bg_color=self._ctx.theme.default_window_bg,
            on_leave=self._cleanup,
        )

    def _cleanup(self) -> None:
        if self._cloud_anim is not None:
            self._cloud_anim.stop()
            self._cloud_anim = None

    def _build(self) -> None:
        if self._ctx.session_manager.is_authenticated():
            self._build_logged_in()
        else:
            self._build_logged_out()

    def _build_logged_out(self) -> None:
        ctx = self._ctx
        theme = ctx.theme
        root = ctx.root

        frame = tk.Frame(root, bg=theme.default_window_bg)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        canvas = tk.Canvas(frame, bg=theme.default_window_bg, highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        self._cloud_anim = start_cloud_animation(
            canvas,
            root,
            ctx.image_registry.get("clouds"),
            config=CloudAnimationConfig(
                count=20,
                speed_min=1.0,
                speed_max=3.0,
                y_max_ratio=0.9,
            ),
        )

        title_wrapper = tk.Frame(canvas, bg=theme.default_window_bg)
        title_wrapper.place(relx=0.5, rely=0.1, anchor="n")
        title_container = tk.Frame(
            title_wrapper, bg=theme.colors.bg_title_logged_out, bd=2, relief=tk.GROOVE
        )
        title_container.pack()
        if ctx.image_registry.get("umbrella"):
            tk.Label(
                title_container,
                image=ctx.image_registry.get("umbrella"),
                bg=theme.colors.bg_title_logged_out,
            ).pack(side="left", padx=5)
        tk.Label(
            title_container,
            text="Clima Mind",
            font=theme.font(theme.main_title_font_size + 4, bold=True),
            bg=theme.colors.bg_title_logged_out,
            fg=theme.colors.fg_title,
        ).pack(side="left", padx=5)

        create_welcome_frame(
            canvas,
            "Welcome to Clima Mind",
            "Discover weather updates, set reminders, and relax with nature sounds.\n"
            "Log in or register to get started!",
            theme,
        ).place(relx=0.5, rely=0.35, anchor="n")

        weather_icon_frame = tk.Frame(canvas, bg=theme.default_window_bg, bd=2, relief=tk.GROOVE)
        weather_icon_frame.place(relx=0.5, rely=0.5, anchor="n")
        for key in ("clouds", "umbrella", "snowy", "contrast"):
            tk.Label(
                weather_icon_frame,
                image=ctx.image_registry.get(key),
                bg=theme.default_window_bg,
            ).pack(side=tk.LEFT, padx=10)

        def click_then(route: str) -> None:
            ctx.sfx_player.play_click()
            self._router.go(route)

        tk.Button(
            canvas,
            text="Log In",
            image=ctx.image_registry.get("login"),
            command=lambda: click_then("login"),
            bg=theme.colors.btn_teal,
            fg=theme.colors.white,
            font=theme.font(theme.base_font_size + 2, bold=True),
            width=200,
            height=50,
            compound="left",
            relief=tk.RAISED,
            padx=15,
        ).place(relx=0.5, rely=0.65, anchor="n", y=-30)

        tk.Button(
            canvas,
            text="Register",
            image=ctx.image_registry.get("register"),
            command=lambda: click_then("register"),
            bg=theme.colors.btn_light_green,
            fg=theme.colors.white,
            font=theme.font(theme.base_font_size + 2, bold=True),
            width=200,
            height=50,
            compound="left",
            relief=tk.RAISED,
            padx=15,
        ).place(relx=0.5, rely=0.65, anchor="n", y=30)

        tk.Button(
            canvas,
            text="Close Application",
            image=ctx.image_registry.get("close"),
            command=self._confirm_close,
            bg=theme.colors.btn_gray,
            fg=theme.colors.white,
            font=theme.font(theme.base_font_size + 1, bold=True),
            width=200,
            height=50,
            compound="left",
            relief=tk.RAISED,
        ).place(relx=0.5, rely=0.95, anchor="s")

    def _build_logged_in(self) -> None:
        ctx = self._ctx
        theme = ctx.theme
        root = ctx.root
        email = ctx.session_manager.email or ""

        frame = tk.Frame(root, bg=theme.default_window_bg)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        top_frame = tk.Frame(frame, bg=theme.colors.bg_settings, bd=2, relief=tk.RAISED)
        top_frame.pack(side="top", fill="x", pady=(5, 10))

        profile_frame = tk.Frame(top_frame, bg=theme.colors.bg_settings, bd=1, relief=tk.SUNKEN)
        profile_frame.pack(side=tk.LEFT, padx=10, pady=10)
        profile_label = tk.Label(profile_frame, bg=theme.colors.bg_settings, cursor="hand2")
        profile_label.pack()
        profile_label.bind(
            "<Button-1>",
            lambda _e: [ctx.sfx_player.play_click(), self._router.go("account_settings")],
        )

        user = ctx.auth_service.get_user(email)
        account_data = user.account if user else None
        if account_data and account_data.profile_picture != "No file selected":
            try:
                img = Image.open(account_data.profile_picture).resize((100, 100))
                photo = ImageTk.PhotoImage(img)
                profile_label.config(image=photo)
                profile_label.image = photo
            except Exception as exc:
                print(f"Profile picture load error (main page): {exc}")
        else:
            profile_label.config(text="", width=10, height=5, relief=tk.RAISED)

        title_frame = tk.Frame(top_frame, bg=theme.colors.bg_settings)
        title_frame.pack(side=tk.TOP, pady=2)
        title_container = tk.Frame(
            title_frame, bg=theme.colors.bg_title_logged_in, bd=2, relief=tk.GROOVE
        )
        title_container.pack()
        if ctx.image_registry.get("umbrella"):
            tk.Label(
                title_container,
                image=ctx.image_registry.get("umbrella"),
                bg=theme.colors.bg_title_logged_in,
            ).pack(side=tk.LEFT, padx=5)
        tk.Label(
            title_container,
            text="Clima Mind",
            font=theme.font(theme.main_title_font_size, bold=True),
            bg=theme.colors.bg_title_logged_in,
            fg=theme.colors.fg_title,
        ).pack(side=tk.LEFT, padx=5)
        title_frame.place(relx=0.5, rely=0.0, anchor="n", y=5)

        top_right = tk.Frame(top_frame, bg=theme.colors.bg_settings, bd=1, relief=tk.SUNKEN)
        top_right.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=5)

        def click_route(route: str) -> None:
            ctx.sfx_player.play_click()
            self._router.go(route)

        tk.Button(
            top_right,
            text="Settings",
            image=ctx.image_registry.get("settings"),
            compound="left",
            command=lambda: click_route("settings"),
            bg="#7986CB",
            fg=theme.colors.white,
            font=theme.font(theme.base_font_size, bold=True),
            relief=tk.RAISED,
            padx=10,
        ).pack(side="left", ipady=2)

        tk.Button(
            top_right,
            text="Logout",
            image=ctx.image_registry.get("logout"),
            compound="left",
            command=self._logout,
            bg=theme.colors.btn_back,
            fg=theme.colors.white,
            font=theme.font(theme.base_font_size, bold=True),
            relief=tk.RAISED,
            padx=10,
        ).pack(side="left", padx=5, ipady=2)

        content = tk.Frame(frame, bg=theme.colors.bg_settings, bd=2, relief=tk.RAISED)
        content.pack(expand=True, fill="both", pady=10)

        username = (account_data.username.strip() if account_data else "") or email.split("@")[0]
        create_welcome_frame(
            content,
            "Clima Mind",
            f"Today will be a perfect day, {username}!\nHow's the weather today?",
            theme,
        ).pack(pady=20, padx=20)

        district_frame = tk.Frame(content, bg=theme.colors.bg_soft_blue, bd=1, relief=tk.SUNKEN)
        district_frame.pack(pady=10, padx=20, fill="x")

        district = account_data.district.strip() if account_data else ""
        if district:
            self._render_district_weather(district_frame, district, theme, ctx)
        else:
            hint = tk.Label(
                district_frame,
                text="📍 Add your district/city in Account Settings for local weather.",
                font=theme.font(theme.base_font_size + 1, italic=True),
                bg=theme.colors.bg_soft_blue,
                fg="blue",
                cursor="hand2",
            )
            hint.pack(padx=10, pady=10)
            hint.bind(
                "<Button-1>",
                lambda _e: [ctx.sfx_player.play_click(), self._router.go("account_settings")],
            )

        actions = tk.Frame(content, bg=theme.colors.bg_settings, bd=1, relief=tk.SUNKEN)
        actions.pack(pady=20)

        for col, (text, route, color, icon_key) in enumerate(
            [
                ("Search Weather", "search_weather", "#64B5F6", "search"),
                ("Set Reminder", "reminder", "#81C784", "reminder"),
                ("Nature Sounds", "music", "#A5D6A7", "music"),
                ("Chat with Joyuci", "joyuci", "#7E57C2", "chat_icon"),
            ]
        ):
            tk.Button(
                actions,
                text=text,
                image=ctx.image_registry.get(icon_key),
                command=lambda r=route: click_route(r),
                bg=color,
                fg=theme.colors.white,
                font=theme.font(theme.base_font_size, bold=True),
                compound="left",
                relief=tk.RAISED,
                padx=10,
            ).grid(row=0, column=col, padx=15, pady=5, ipady=5)

        close_frame = tk.Frame(content, bg=theme.colors.bg_settings, bd=1, relief=tk.SUNKEN)
        close_frame.pack(pady=10)
        tk.Button(
            close_frame,
            text="Close Application",
            image=ctx.image_registry.get("close"),
            command=self._confirm_close,
            bg=theme.colors.btn_gray,
            fg=theme.colors.white,
            width=200,
            height=40,
            compound="left",
            font=theme.font(theme.base_font_size + 1, bold=True),
            relief=tk.RAISED,
        ).pack(pady=10)

    def _render_district_weather(self, parent: tk.Frame, district: str, theme, ctx) -> None:
        try:
            weather = ctx.weather_client.fetch_current(district)
        except WeatherError:
            tk.Label(
                parent,
                text=f"Could not fetch weather for '{district}'.",
                font=theme.font(theme.base_font_size + 1, italic=True),
                bg=theme.colors.bg_soft_blue,
            ).pack(padx=10, pady=10)
            return

        icon_map = {
            "rain": "umbrella",
            "snow": "snowy",
            "clear": "contrast",
            "clouds": "clouds",
            "mist": "fog",
            "fog": "fog",
            "haze": "fog",
        }
        icon_key = icon_map.get(weather.main, "clouds")
        icon_label = tk.Label(parent, bg=theme.colors.bg_soft_blue)
        icon_img = ctx.image_registry.get(icon_key)
        if icon_img:
            try:
                small = icon_img._PhotoImage__photo.subsample(2, 2)
                icon_label.config(image=small)
                icon_label.image = small
            except Exception:
                icon_label.config(image=icon_img)
                icon_label.image = icon_img
        icon_label.pack(side=tk.LEFT, padx=10, pady=5)
        tk.Label(
            parent,
            text=f"{district}: {weather.description}, {weather.temp:.1f}°C",
            font=theme.font(13),
            bg=theme.colors.bg_soft_blue,
        ).pack(side=tk.LEFT, padx=10, pady=5)

    def _logout(self) -> None:
        ctx = self._ctx
        ctx.sfx_player.play_click()
        if messagebox.askyesno("Log Out", "Are you sure you want to log out?"):
            ctx.auth_service.logout()
            self.show()

    def _confirm_close(self) -> None:
        self._ctx.sfx_player.play_click()
        if messagebox.askyesno("Confirm Close", "Are you sure you want to close the application?"):
            if self._ctx.music_player.current_track:
                self._ctx.music_player.stop()
            self._ctx.root.destroy()


def show_main_menu(ctx: AppContext) -> None:
    MainMenuView(ctx).show()
