"""Login screen."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from climamind.context import AppContext
from climamind.ui.views.main_menu_view import MainMenuView
from climamind.infrastructure.email.smtp_email_sender import EmailError
from climamind.services.exceptions import (
    AuthError,
    EmailNotVerifiedError,
    InvalidCredentialsError,
)
from climamind.ui.views.helpers import (
    build_fullscreen_canvas,
    create_welcome_frame,
    load_eye_icons,
    panel_bg,
)
from climamind.ui.widgets.back_button import create_back_button
from climamind.ui.widgets.cloud_animation import CloudAnimation


class LoginView:
    def __init__(self, ctx: AppContext) -> None:
        self._ctx = ctx
        self._cloud_anim: CloudAnimation | None = None

    def show(self) -> None:
        self._ctx.navigation.navigate(
            self._build,
            view_name="login",
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
            "Log In to Clima Mind",
            "Enter your credentials to access your account.",
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

        email_entry = self._labeled_entry(container, panel, theme, "Email:")
        password_entry = self._labeled_entry(
            container, panel, theme, "Password:", show="*"
        )
        email_entry.focus()

        eye_icon, eye_off_icon = load_eye_icons(root)

        def toggle_password() -> None:
            if password_entry.cget("show") == "*":
                password_entry.config(show="")
                show_button.config(image=eye_off_icon)
                show_button.image = eye_off_icon
            else:
                password_entry.config(show="*")
                show_button.config(image=eye_icon)
                show_button.image = eye_icon

        password_frame = password_entry.master
        show_button = tk.Button(
            password_frame,
            image=eye_icon,
            command=lambda: [ctx.sfx_player.play_click(), toggle_password()],
            bg=panel,
            relief=tk.FLAT,
        )
        show_button.pack(side=tk.LEFT, padx=5)

        def on_email_enter(_event=None) -> None:
            ctx.sfx_player.play_field_complete()
            password_entry.focus_set()

        email_entry.bind("<Return>", on_email_enter)
        password_entry.bind("<Return>", lambda _e: submit_login())

        def submit_login() -> None:
            ctx.sfx_player.play_click()
            email = email_entry.get().strip().lower()
            password = password_entry.get()
            try:
                display = ctx.auth_service.login(email, password)
                ctx.sfx_player.play_success()
                messagebox.showinfo("Success", f"Welcome back, {display}!")
                MainMenuView(ctx).show()
            except EmailNotVerifiedError as exc:
                ctx.sfx_player.play_error()
                messagebox.showerror("Error", str(exc))
            except InvalidCredentialsError as exc:
                ctx.sfx_player.play_error()
                messagebox.showerror("Error", str(exc))
            except AuthError as exc:
                ctx.sfx_player.play_error()
                messagebox.showerror("Error", str(exc))

        def forgot_password() -> None:
            ctx.sfx_player.play_click()
            email = email_entry.get().strip().lower()
            try:
                ctx.auth_service.request_password_reset(email)
                messagebox.showinfo(
                    "Success",
                    f"Password reset instructions have been sent to {email}.",
                )
                from climamind.ui.views.change_password_view import ResetPasswordView

                ResetPasswordView(ctx, email).show()
            except AuthError as exc:
                messagebox.showerror("Error", str(exc))
            except EmailError as exc:
                messagebox.showerror("Error", f"Failed to send email: {exc}")

        button_frame = tk.Frame(container, bg=panel)
        button_frame.pack(pady=15)
        tk.Button(
            button_frame,
            text="Log In",
            command=submit_login,
            **theme.large_button_style(),
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            button_frame,
            text="Forgot Password",
            image=ctx.image_registry.get("password"),
            compound="left",
            command=forgot_password,
            bg="#FF8A65",
            fg="white",
            font=theme.font(theme.large_font_size, bold=True),
            relief=tk.RAISED,
        ).pack(side=tk.LEFT, padx=5)

        create_back_button(
            container,
            lambda: MainMenuView(ctx).show(),
            theme=theme,
            images=ctx.image_registry,
            sfx_player=ctx.sfx_player,
        )

    @staticmethod
    def _labeled_entry(
        parent: tk.Frame,
        panel_bg_color: str,
        theme,
        label: str,
        show: str | None = None,
    ) -> tk.Entry:
        frame = tk.Frame(parent, bg=panel_bg_color)
        frame.pack(pady=5)
        tk.Label(
            frame,
            text=label,
            font=theme.font(theme.large_font_size),
            bg=panel_bg_color,
        ).pack(side=tk.LEFT, padx=5)
        kwargs = theme.large_entry_style()
        if show is not None:
            kwargs["show"] = show
        entry = tk.Entry(frame, **kwargs)
        entry.pack(side=tk.LEFT, padx=5)
        return entry


def show_login(ctx: AppContext) -> None:
    LoginView(ctx).show()
