"""Account profile settings screen."""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image, ImageTk

from climamind.context import AppContext
from climamind.infrastructure.api.openweather_client import WeatherError
from climamind.services.account_service import AccountError, NotAuthenticatedError
from climamind.ui.views.auth_guard import require_email
from climamind.ui.views.helpers import create_welcome_frame, entry_style_copy, panel_bg
from climamind.ui.views.main_menu_view import MainMenuView
from climamind.ui.widgets.back_button import BackButtonPlacement, create_back_button
from climamind.ui.widgets.cloud_animation import CloudAnimationConfig, start_cloud_animation


class AccountSettingsView:
    def __init__(self, ctx: AppContext) -> None:
        self._ctx = ctx
        self._cloud_anim = None
        self._preview_photo = None

    def show(self) -> None:
        if not require_email(self._ctx, lambda: MainMenuView(self._ctx).show()):
            return
        self._ctx.navigation.navigate(
            self._build,
            view_name="account_settings",
            on_leave=self._cleanup,
        )

    def _open_settings(self) -> None:
        from climamind.ui.views.settings_view import SettingsView

        SettingsView(self._ctx).show()

    def _cleanup(self) -> None:
        if self._cloud_anim is not None:
            self._cloud_anim.stop()
            self._cloud_anim = None

    def _build(self) -> None:
        ctx = self._ctx
        theme = ctx.theme
        root = ctx.root
        email = ctx.session_manager.email or ""
        panel = panel_bg(theme)
        bg = theme.default_window_bg

        try:
            user = ctx.account_service.get_profile(email)
        except NotAuthenticatedError:
            MainMenuView(ctx).show()
            return

        outer = tk.Frame(root, bg=bg)
        outer.pack(fill="both", expand=True, padx=20, pady=20)

        canvas = tk.Canvas(outer, bg=bg, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        self._cloud_anim = start_cloud_animation(
            canvas, root, ctx.image_registry.get("clouds")
        )

        create_welcome_frame(
            canvas,
            "Account Settings",
            "Update your profile, district, and picture.",
            theme,
        ).place(relx=0.5, rely=0.08, anchor="n")

        district = user.account.district.strip()
        if district:
            try:
                weather = ctx.weather_client.fetch_current(district)
                weather_bar = tk.Frame(canvas, bg=panel, bd=2, relief=tk.GROOVE)
                weather_bar.place(relx=0.5, rely=0.16, anchor="center")
                icon_key = {
                    "rain": "umbrella",
                    "snow": "snowy",
                    "clear": "contrast",
                    "clouds": "clouds",
                }.get(weather.main.lower(), "clouds")
                icon = ctx.image_registry.get(icon_key)
                if icon:
                    tk.Label(weather_bar, image=icon, bg=panel).pack(side=tk.LEFT, padx=5)
                tk.Label(
                    weather_bar,
                    text=f"{district}: {weather.description.capitalize()}, {weather.temp:.1f}°C",
                    font=theme.font(theme.base_font_size + 1),
                    bg=panel,
                ).pack(side=tk.LEFT, padx=5)
            except WeatherError:
                pass

        container = tk.Frame(canvas, bg=panel, bd=2, relief=tk.GROOVE, padx=25, pady=25)
        container.place(relx=0.5, rely=0.5, anchor="center")

        preview = tk.Label(container, bg=panel, bd=2, relief=tk.RIDGE)
        preview.pack(pady=10)
        path_label = tk.Label(
            container,
            text=user.account.profile_picture,
            bg=panel,
            fg="grey",
            font=theme.font(theme.base_font_size),
            wraplength=400,
        )
        path_label.pack(pady=5)

        def show_preview(path: str) -> None:
            if not path or path == "No file selected":
                preview.config(image="")
                return
            try:
                img = Image.open(path).resize((150, 150))
                self._preview_photo = ImageTk.PhotoImage(img, master=root)
                preview.config(image=self._preview_photo)
            except Exception as exc:
                print(f"Profile preview error: {exc}")

        show_preview(user.account.profile_picture)

        def browse() -> None:
            path = filedialog.askopenfilename(
                title="Select Profile Picture",
                filetypes=[("Image Files", "*.png;*.jpg;*.jpeg"), ("All Files", "*.*")],
            )
            if path:
                path_label.config(text=path, fg="black")
                show_preview(path)

        tk.Button(
            container,
            text="Browse...",
            command=browse,
            bg=theme.colors.btn_green,
            fg=theme.colors.white,
            font=theme.font(theme.base_font_size, bold=True),
        ).pack(pady=5)

        tk.Label(
            container,
            text="Username:",
            font=theme.font(theme.large_font_size - 1, bold=True),
            bg=panel,
        ).pack(anchor="w")
        username_entry = tk.Entry(
            container, **entry_style_copy(theme), width=40
        )
        username_entry.pack(pady=5)
        username_entry.insert(0, user.account.username)

        tk.Label(
            container,
            text="District/City:",
            font=theme.font(theme.large_font_size - 1, bold=True),
            bg=panel,
        ).pack(anchor="w", pady=(10, 0))
        district_entry = tk.Entry(
            container, **entry_style_copy(theme), width=40
        )
        district_entry.pack(pady=5)
        district_entry.insert(0, user.account.district)

        def save() -> None:
            ctx.sfx_player.play_click()
            try:
                changed = ctx.account_service.update_profile(
                    email,
                    username=username_entry.get().strip(),
                    district=district_entry.get().strip(),
                    profile_picture=path_label.cget("text"),
                )
            except AccountError as exc:
                messagebox.showerror("Error", str(exc))
                return
            if changed:
                messagebox.showinfo("Success", "Account information saved!")
                MainMenuView(ctx).show()
            else:
                messagebox.showinfo("Information", "No changes were made.")
                self._open_settings()

        tk.Button(
            container,
            text="Save Information",
            bg=theme.colors.btn_green,
            fg=theme.colors.white,
            font=theme.font(theme.base_font_size + 1, bold=True),
            command=save,
        ).pack(pady=20)

        create_back_button(
            outer,
            self._open_settings,
            theme=theme,
            images=ctx.image_registry,
            sfx_player=ctx.sfx_player,
            placement=BackButtonPlacement.BOTTOM_CENTER,
        )
