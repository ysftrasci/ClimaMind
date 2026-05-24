"""Logged-in password change screen."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from climamind.context import AppContext
from climamind.services.exceptions import (
    AuthError,
    EmptyFieldsError,
    InvalidCredentialsError,
    NotAuthenticatedError,
    PasswordMismatchError,
    PasswordTooShortError,
)
from climamind.ui.views.auth_guard import require_email
from climamind.ui.views.helpers import (
    build_fullscreen_canvas,
    create_welcome_frame,
    panel_bg,
)
from climamind.ui.views.main_menu_view import MainMenuView
from climamind.ui.widgets.back_button import BackButtonPlacement, create_back_button
from climamind.ui.widgets.cloud_animation import CloudAnimation


class SettingsChangePasswordView:
    def __init__(self, ctx: AppContext) -> None:
        self._ctx = ctx
        self._cloud_anim: CloudAnimation | None = None
    def show(self) -> None:
        if not require_email(self._ctx, lambda: MainMenuView(self._ctx).show()):
            return
        self._ctx.navigation.navigate(
            self._build,
            view_name="change_password",
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
        panel = panel_bg(theme)
        email = ctx.session_manager.email or ""

        canvas, self._cloud_anim = build_fullscreen_canvas(root, theme, ctx.image_registry)
        create_welcome_frame(
            canvas,
            "Change Password",
            "Enter your current password and choose a new one.",
            theme,
        ).place(relx=0.5, rely=0.1, anchor="n")

        box = tk.Frame(canvas, bg=panel, bd=2, relief=tk.RAISED, padx=20, pady=20)
        box.place(relx=0.5, rely=0.5, anchor="center")

        current_entry = self._field(box, panel, theme, "Current Password:", show="*")
        new_entry = self._field(box, panel, theme, "New Password:", show="*")
        confirm_entry = self._field(box, panel, theme, "Confirm New Password:", show="*")

        def submit() -> None:
            ctx.sfx_player.play_click()
            try:
                ctx.auth_service.change_password(
                    email,
                    current_entry.get(),
                    new_entry.get(),
                    confirm_entry.get(),
                )
                messagebox.showinfo("Success", "Password changed successfully!")
                self._open_settings()
            except (
                NotAuthenticatedError,
                EmptyFieldsError,
                PasswordMismatchError,
                InvalidCredentialsError,
                PasswordTooShortError,
                AuthError,
            ) as exc:
                messagebox.showerror("Error", str(exc))

        tk.Button(
            box,
            text="Change Password",
            bg=theme.colors.btn_green,
            fg=theme.colors.white,
            font=theme.font(theme.large_font_size, bold=True),
            command=submit,
        ).pack(pady=15)

        create_back_button(
            canvas,
            self._open_settings,
            theme=theme,
            images=ctx.image_registry,
            sfx_player=ctx.sfx_player,
            placement=BackButtonPlacement.BOTTOM_CENTER,
        )

    @staticmethod
    def _field(
        parent: tk.Frame,
        panel: str,
        theme,
        label: str,
        *,
        show: str = "",
    ) -> tk.Entry:
        tk.Label(
            parent,
            text=label,
            font=theme.font(theme.base_font_size + 1),
            bg=panel,
        ).pack(anchor="w", pady=(8, 0))
        entry = tk.Entry(parent, show=show, font=theme.font(theme.large_font_size), width=35)
        entry.pack(pady=4)
        return entry
