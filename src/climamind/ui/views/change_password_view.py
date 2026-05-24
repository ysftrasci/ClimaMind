"""Password reset screen (forgot password flow — reset code + new password)."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from climamind.context import AppContext
from climamind.services.exceptions import (
    AuthError,
    EmptyFieldsError,
    InvalidResetCodeError,
    PasswordMismatchError,
)
from climamind.ui.views.helpers import (
    build_fullscreen_canvas,
    create_welcome_frame,
    panel_bg,
)
from climamind.ui.views.login_view import LoginView
from climamind.ui.widgets.back_button import create_back_button
from climamind.ui.widgets.cloud_animation import CloudAnimation


class ResetPasswordView:
    """
    Şifremi unuttum akışı: e-posta ile gelen kod + yeni şifre.

    (Ayarlar menüsündeki oturum açıkken şifre değiştirme ekranı 7B'de eklenecek.)
    """

    def __init__(self, ctx: AppContext, email: str) -> None:
        self._ctx = ctx
        self._email = email.strip().lower()
        self._cloud_anim: CloudAnimation | None = None

    def show(self) -> None:
        self._ctx.navigation.navigate(
            self._build,
            view_name="reset_password",
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
            "Reset Your Password",
            "Enter the reset code and your new password.",
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

        entries: dict[str, tk.Entry] = {}
        for label_text, show_char, name in [
            ("Reset Code:", "", "code"),
            ("New Password:", "*", "password"),
            ("Confirm Password:", "*", "confirm"),
        ]:
            row = tk.Frame(container, bg=panel)
            row.pack(pady=5)
            tk.Label(
                row,
                text=label_text,
                font=theme.font(theme.large_font_size),
                bg=panel,
            ).pack(side=tk.LEFT, padx=5)
            entry = tk.Entry(
                row,
                show=show_char,
                font=theme.font(theme.large_font_size),
                bg=theme.colors.white,
                fg=theme.colors.fg_body,
                insertbackground=theme.colors.fg_body,
            )
            entry.pack(side=tk.LEFT, padx=5)
            entries[name] = entry

        entries["code"].focus()

        def submit_reset() -> None:
            ctx.sfx_player.play_click()
            try:
                ctx.auth_service.reset_password(
                    self._email,
                    entries["code"].get().strip(),
                    entries["password"].get().strip(),
                    entries["confirm"].get().strip(),
                )
                ctx.sfx_player.play_success()
                messagebox.showinfo(
                    "Success", "Your password has been successfully reset!"
                )
                LoginView(ctx).show()
            except (EmptyFieldsError, InvalidResetCodeError, PasswordMismatchError) as exc:
                messagebox.showerror("Error", str(exc))
            except AuthError as exc:
                messagebox.showerror("Error", str(exc))

        button_frame = tk.Frame(container, bg=panel)
        button_frame.pack(pady=15)
        tk.Button(
            button_frame,
            text="Reset Password",
            command=submit_reset,
            bg=theme.colors.btn_joyuci,
            fg=theme.colors.white,
            font=theme.font(theme.large_font_size, bold=True),
            relief=tk.RAISED,
        ).pack(side=tk.LEFT, padx=5)

        create_back_button(
            container,
            lambda: LoginView(ctx).show(),
            theme=theme,
            images=ctx.image_registry,
            sfx_player=ctx.sfx_player,
        )


def show_reset_password(ctx: AppContext, email: str) -> None:
    ResetPasswordView(ctx, email).show()
