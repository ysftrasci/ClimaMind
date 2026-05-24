"""Settings hub screen."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from climamind.context import AppContext
from climamind.services.exceptions import AuthError, UserNotFoundError
from climamind.ui.views.auth_guard import require_email
from climamind.ui.views.account_settings_view import AccountSettingsView
from climamind.ui.views.favorites_view import FavoritesView
from climamind.ui.views.main_menu_view import MainMenuView
from climamind.ui.views.settings_change_password_view import SettingsChangePasswordView
from climamind.ui.widgets.back_button import create_back_button


class SettingsView:
    def __init__(self, ctx: AppContext) -> None:
        self._ctx = ctx

    def show(self) -> None:
        if not require_email(self._ctx, lambda: MainMenuView(self._ctx).show()):
            return
        self._ctx.navigation.navigate(
            self._build,
            view_name="settings",
            bg_color=self._ctx.theme.colors.bg_settings,
        )

    def _build(self) -> None:
        ctx = self._ctx
        theme = ctx.theme
        root = ctx.root
        bg = theme.colors.bg_settings

        frame = tk.Frame(root, bg=bg)
        frame.pack(fill="both", expand=True, padx=40, pady=40)

        tk.Label(
            frame,
            text="Settings",
            font=theme.font(theme.main_title_font_size + 2, bold=True),
            bg=bg,
            fg="#1A237E",
        ).pack(pady=20)

        container = tk.Frame(frame, bg=bg)
        container.pack(pady=10)

        btn_style = {
            "width": 350,
            "compound": "left",
            "padx": 10,
            "height": 2,
            "font": theme.font(14, bold=True),
            "fg": theme.colors.white,
            "relief": tk.RAISED,
        }

        def open_view(show_fn) -> None:
            ctx.sfx_player.play_click()
            show_fn()

        tk.Button(
            container,
            text="Account Settings",
            image=ctx.image_registry.get("account_icon"),
            command=lambda: open_view(lambda: AccountSettingsView(ctx).show()),
            bg="#64B5F6",
            **btn_style,
        ).pack(pady=7)
        tk.Button(
            container,
            text="Favorite Cities",
            image=ctx.image_registry.get("favourite_icon"),
            command=lambda: open_view(lambda: FavoritesView(ctx).show()),
            bg="#7986CB",
            **btn_style,
        ).pack(pady=7)
        tk.Button(
            container,
            text="Change Password",
            image=ctx.image_registry.get("password"),
            command=lambda: open_view(lambda: SettingsChangePasswordView(ctx).show()),
            bg="#9575CD",
            **btn_style,
        ).pack(pady=7)
        tk.Button(
            container,
            text="Delete Account",
            image=ctx.image_registry.get("delete"),
            command=self._delete_account,
            bg="#E57373",
            **btn_style,
        ).pack(pady=7)

        create_back_button(
            frame,
            lambda: MainMenuView(ctx).show(),
            theme=theme,
            images=ctx.image_registry,
            sfx_player=ctx.sfx_player,
        )

    def _delete_account(self) -> None:
        ctx = self._ctx
        email = ctx.session_manager.email
        if not email:
            return
        ctx.sfx_player.play_click()
        if not messagebox.askyesno(
            "Delete Account",
            "You are about to delete your account. This action cannot be undone!\n\n"
            "All your data (favorites, settings, reminders) will be permanently deleted.\n\n"
            "Are you sure you want to proceed?",
            icon="warning",
        ):
            return
        try:
            ctx.auth_service.delete_account(email)
            messagebox.showinfo("Account Deleted", "Your account has been deleted.")
            MainMenuView(ctx).show()
        except (UserNotFoundError, AuthError) as exc:
            messagebox.showerror("Error", str(exc))
