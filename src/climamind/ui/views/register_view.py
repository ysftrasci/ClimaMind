"""User registration screen."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from climamind.context import AppContext
from climamind.infrastructure.email.smtp_email_sender import EmailError
from climamind.services.exceptions import (
    AuthError,
    EmptyFieldsError,
    PasswordMismatchError,
    UserAlreadyExistsError,
)
from climamind.ui.views.helpers import (
    build_fullscreen_canvas,
    create_welcome_frame,
    load_eye_icons,
    panel_bg,
)
from climamind.ui.views.main_menu_view import MainMenuView
from climamind.ui.views.verify_email_view import VerifyEmailView
from climamind.ui.widgets.back_button import create_back_button
from climamind.ui.widgets.cloud_animation import CloudAnimation


class RegisterView:
    def __init__(self, ctx: AppContext) -> None:
        self._ctx = ctx
        self._cloud_anim: CloudAnimation | None = None

    def show(self) -> None:
        self._ctx.navigation.navigate(
            self._build,
            view_name="register",
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
            "Register for Clima Mind",
            "Create an account to get started!",
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

        email_entry = _entry_row(container, panel, theme, "Email:")
        password_entry = _entry_row(container, panel, theme, "Password:", show="*")
        confirm_entry = _entry_row(container, panel, theme, "Confirm Password:", show="*")
        email_entry.focus()

        eye_icon, eye_off_icon = load_eye_icons(root)

        def toggle_password() -> None:
            if password_entry.cget("show") == "*":
                password_entry.config(show="")
                confirm_entry.config(show="")
                show_button.config(image=eye_off_icon)
                show_button.image = eye_off_icon
            else:
                password_entry.config(show="*")
                confirm_entry.config(show="*")
                show_button.config(image=eye_icon)
                show_button.image = eye_icon

        show_button = tk.Button(
            confirm_entry.master,
            image=eye_icon,
            command=lambda: [ctx.sfx_player.play_click(), toggle_password()],
            bg=panel,
            relief=tk.FLAT,
        )
        show_button.pack(side=tk.LEFT, padx=5)

        def on_field_enter(_event, next_widget) -> None:
            ctx.sfx_player.play_field_complete()
            next_widget.focus_set()

        email_entry.bind("<Return>", lambda e: on_field_enter(e, password_entry))
        password_entry.bind("<Return>", lambda e: on_field_enter(e, confirm_entry))
        confirm_entry.bind("<Return>", lambda _e: submit_register())

        def submit_register() -> None:
            ctx.sfx_player.play_click()
            try:
                email = ctx.auth_service.register(
                    email_entry.get(),
                    password_entry.get(),
                    confirm_entry.get(),
                )
                VerifyEmailView(ctx, email).show()
            except (EmptyFieldsError, PasswordMismatchError, UserAlreadyExistsError) as exc:
                ctx.sfx_player.play_error()
                messagebox.showerror("Error", str(exc))
            except EmailError as exc:
                ctx.sfx_player.play_error()
                messagebox.showerror("Error", f"Failed to send verification email: {exc}")
            except AuthError as exc:
                ctx.sfx_player.play_error()
                messagebox.showerror("Error", str(exc))

        tk.Button(
            container,
            text="Register",
            command=submit_register,
            **theme.large_button_style(),
        ).pack(pady=15)

        create_back_button(
            container,
            lambda: MainMenuView(ctx).show(),
            theme=theme,
            images=ctx.image_registry,
            sfx_player=ctx.sfx_player,
        )


def _entry_row(
    parent: tk.Frame,
    panel: str,
    theme,
    label: str,
    show: str | None = None,
) -> tk.Entry:
    frame = tk.Frame(parent, bg=panel)
    frame.pack(pady=5)
    tk.Label(frame, text=label, font=theme.font(theme.large_font_size), bg=panel).pack(
        side=tk.LEFT, padx=5
    )
    kwargs = theme.large_entry_style()
    if show:
        kwargs["show"] = show
    entry = tk.Entry(frame, **kwargs)
    entry.pack(side=tk.LEFT, padx=5)
    return entry


def show_register(ctx: AppContext) -> None:
    RegisterView(ctx).show()
