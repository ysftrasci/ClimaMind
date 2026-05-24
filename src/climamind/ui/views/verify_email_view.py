"""Email verification screen after registration."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from climamind.context import AppContext
from climamind.services.exceptions import AuthError, VerificationCodeError
from climamind.ui.views.helpers import (
    build_fullscreen_canvas,
    create_welcome_frame,
    entry_style_copy,
    panel_bg,
)
from climamind.ui.views.login_view import LoginView
from climamind.ui.views.main_menu_view import MainMenuView
from climamind.ui.widgets.back_button import create_back_button
from climamind.ui.widgets.cloud_animation import CloudAnimation


class VerifyEmailView:
    def __init__(self, ctx: AppContext, email: str) -> None:
        self._ctx = ctx
        self._email = email.strip().lower()
        self._cloud_anim: CloudAnimation | None = None

    def show(self) -> None:
        self._ctx.navigation.navigate(
            self._build,
            view_name="verify_email",
            bg_color=self._ctx.theme.default_window_bg,
            on_leave=self._cleanup,
        )

    def _cleanup(self) -> None:
        if self._cloud_anim is not None:
            self._cloud_anim.stop()
            self._cloud_anim = None

    def _build(self) -> None:
        ctx = self._ctx
        theme = ctx.theme
        root = ctx.root
        panel = panel_bg(theme)

        canvas, self._cloud_anim = build_fullscreen_canvas(root, theme, ctx.image_registry)
        create_welcome_frame(
            canvas,
            "Verify Your Email",
            f"Enter the 6-digit code sent to {self._email}",
            theme,
        ).place(relx=0.5, rely=0.1, anchor="n")

        container = tk.Frame(canvas, bg=panel, bd=2, relief=tk.RAISED, padx=20, pady=20)
        container.place(relx=0.5, rely=0.5, anchor="center")

        icon_frame = tk.Frame(container, bg=panel)
        icon_frame.pack(pady=10)
        for key in ("clouds", "umbrella", "snowy"):
            tk.Label(icon_frame, image=ctx.image_registry.get(key), bg=panel).pack(
                side=tk.LEFT, padx=10
            )

        code_frame = tk.Frame(container, bg=panel)
        code_frame.pack(pady=10)
        tk.Label(
            code_frame,
            text="Verification Code:",
            font=theme.font(theme.large_font_size),
            bg=panel,
        ).pack(side=tk.LEFT, padx=5)
        code_entry = tk.Entry(
            code_frame,
            justify="center",
            **entry_style_copy(theme, width=10),
        )
        code_entry.pack(side=tk.LEFT, padx=5)
        code_entry.focus()

        def verify_code() -> None:
            ctx.sfx_player.play_click()
            try:
                ctx.auth_service.verify_registration(
                    self._email, code_entry.get().strip()
                )
                ctx.sfx_player.play_register_success()
                messagebox.showinfo(
                    "Success",
                    "Your email address has been verified! You can now log in.",
                )
                LoginView(ctx).show()
            except VerificationCodeError as exc:
                ctx.sfx_player.play_error()
                messagebox.showerror("Error", str(exc))
            except AuthError as exc:
                ctx.sfx_player.play_error()
                messagebox.showerror("Error", str(exc))

        code_entry.bind("<Return>", lambda _e: verify_code())
        tk.Button(
            container,
            text="Verify",
            command=verify_code,
            **theme.large_button_style(),
        ).pack(pady=15)

        create_back_button(
            container,
            lambda: MainMenuView(ctx).show(),
            theme=theme,
            images=ctx.image_registry,
            sfx_player=ctx.sfx_player,
        )


def show_verify_email(ctx: AppContext, email: str) -> None:
    VerifyEmailView(ctx, email).show()
