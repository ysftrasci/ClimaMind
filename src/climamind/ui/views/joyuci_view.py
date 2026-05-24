"""Joyuci chat assistant screen."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, scrolledtext

from climamind.context import AppContext
from climamind.services.exceptions import EmptyQueryError
from climamind.ui.views.auth_guard import require_email
from climamind.ui.views.helpers import create_welcome_frame, panel_bg
from climamind.ui.views.main_menu_view import MainMenuView
from climamind.ui.views.share_helper import execute_share
from climamind.ui.widgets.back_button import BackButtonPlacement, create_back_button
from climamind.ui.widgets.weather_animations import WeatherAnimation
from climamind.ui.widgets.weekly_chart import render_weekly_chart


class JoyuciView:
    def __init__(self, ctx: AppContext) -> None:
        self._ctx = ctx
        self._weather_anim: WeatherAnimation | None = None
        self._chart_widget = None

    def show(self) -> None:
        email = require_email(self._ctx, lambda: MainMenuView(self._ctx).show())
        if not email:
            return
        if self._ctx.music_player.current_track:
            self._ctx.music_player.stop()
        self._ctx.music_player.page_active = False
        self._ctx.navigation.navigate(
            self._build,
            view_name="joyuci",
            on_leave=self._cleanup,
        )

    def _cleanup(self) -> None:
        if self._weather_anim is not None:
            self._weather_anim.stop()
            self._weather_anim = None
        self._chart_widget = None

    def _build(self) -> None:
        ctx = self._ctx
        theme = ctx.theme
        root = ctx.root
        email = ctx.session_manager.email or ""
        user = ctx.auth_service.get_user(email)
        username = ""
        if user and user.account.username.strip():
            username = user.account.username.strip()
        else:
            username = email.split("@")[0]

        panel = panel_bg(theme)
        bg = theme.default_window_bg

        frame = tk.Frame(root, bg=bg)
        frame.pack(fill="both", expand=True, padx=20, pady=10)

        create_welcome_frame(
            frame,
            f"Hey {username}, I'm Joyuci! 😊",
            "Your friendly weather buddy is here to help!",
            theme,
        ).pack(pady=10)

        history_frame = tk.Frame(frame, bg=theme.colors.bg_soft_blue, bd=1, relief=tk.SUNKEN)
        history_frame.pack(pady=10, padx=10, fill="x")

        header = tk.Frame(history_frame, bg=theme.colors.bg_soft_blue)
        header.pack(fill="x", padx=10, pady=5)
        tk.Label(
            header,
            text="Chat History",
            font=theme.font(theme.large_font_size, bold=True),
            bg=theme.colors.bg_soft_blue,
            fg="#006064",
        ).pack(side=tk.LEFT)

        chat_text = scrolledtext.ScrolledText(
            history_frame,
            height=6,
            font=theme.font(theme.base_font_size + 1),
            wrap=tk.WORD,
            state=tk.DISABLED,
        )
        chat_text.pack(padx=10, pady=5, fill="x")

        def load_history() -> None:
            history = ctx.joyuci_service.get_chat_history(email)
            text = ctx.joyuci_service.format_chat_history_text(history)
            chat_text.config(state=tk.NORMAL)
            chat_text.delete("1.0", tk.END)
            chat_text.insert(tk.END, text)
            chat_text.config(state=tk.DISABLED)
            chat_text.see(tk.END)

        def clear_history() -> None:
            if messagebox.askyesno(
                "Confirm",
                "Are you sure you want to clear your chat history? This cannot be undone.",
            ):
                ctx.sfx_player.play_click()
                ctx.joyuci_service.clear_chat_history(email)
                load_history()

        tk.Button(
            header,
            text="Clear Chat History",
            command=lambda: [ctx.sfx_player.play_click(), clear_history()],
            bg="#F44336",
            fg=theme.colors.white,
            font=theme.font(theme.base_font_size, bold=True),
        ).pack(side=tk.RIGHT, padx=5)

        load_history()

        guide = tk.Frame(frame, bg=theme.colors.bg_soft_blue, bd=1, relief=tk.SUNKEN)
        guide.pack(pady=10, padx=10, fill="x")
        tk.Label(
            guide,
            text="Try asking me:",
            font=theme.font(theme.large_font_size, bold=True),
            bg=theme.colors.bg_soft_blue,
            fg="#006064",
        ).pack(anchor="w", padx=10, pady=5)
        for q in [
            "Weekly forecast for İstanbul",
            "Is it dangerous in Beykoz?",
            "What to do in Beylikdüzü?",
        ]:
            tk.Label(
                guide,
                text=f"- {q}",
                font=theme.font(theme.base_font_size + 1),
                bg=theme.colors.bg_soft_blue,
            ).pack(anchor="w", padx=20, pady=2)

        input_frame = tk.Frame(frame, bg=bg)
        input_frame.pack(pady=10, fill="x")
        tk.Label(
            input_frame,
            text="Ask me anything about weather or fun things to do!",
            font=theme.font(theme.large_font_size),
            bg=bg,
            fg="#006064",
        ).pack(anchor="w", padx=5)
        query_entry = tk.Entry(
            input_frame,
            font=theme.font(theme.large_font_size),
            width=50,
            bg=theme.colors.white,
        )
        query_entry.pack(padx=20, pady=10, fill="x")
        query_entry.focus()

        result_frame = tk.Frame(frame, bg=theme.colors.bg_soft_blue, bd=1, relief=tk.SUNKEN)
        result_frame.pack(pady=10, padx=10, fill="both", expand=True)
        anim_holder = tk.Frame(result_frame, bg=theme.colors.bg_soft_blue)
        anim_holder.pack(fill="x")
        self._weather_anim = WeatherAnimation(anim_holder, theme=theme)
        result_content = tk.Frame(result_frame, bg=theme.colors.bg_soft_blue)
        result_content.pack(fill="both", expand=True, padx=10, pady=5)

        def clear_result() -> None:
            for w in result_content.winfo_children():
                w.destroy()
            if self._weather_anim:
                self._weather_anim.stop()
            self._chart_widget = None

        def submit() -> None:
            ctx.sfx_player.play_click()
            query = query_entry.get().strip()
            try:
                response = ctx.joyuci_service.process_query(email, query, username)
            except EmptyQueryError as exc:
                messagebox.showwarning("Oops!", str(exc))
                return

            clear_result()
            load_history()

            tk.Label(
                result_content,
                text=response.response_text,
                font=theme.font(theme.base_font_size + 1),
                bg=theme.colors.bg_soft_blue,
                wraplength=700,
                justify=tk.LEFT,
            ).pack(anchor="w", pady=5)

            if response.weekly_forecast and response.city:
                self._chart_widget = render_weekly_chart(
                    result_content,
                    response.weekly_forecast,
                    response.city,
                )

            if response.current_weather:
                self._weather_anim.start(response.current_weather)
                city = response.city or ""
                share_row = tk.Frame(result_content, bg=theme.colors.bg_soft_blue)
                share_row.pack(anchor="w", pady=8)
                for text, color, platform in [
                    ("Instagram", "#E1306C", "instagram"),
                    ("WhatsApp", "#25D366", "whatsapp"),
                    ("LinkedIn", "#0077B5", "linkedin"),
                    ("X", "#000000", "x"),
                ]:
                    tk.Button(
                        share_row,
                        text=text,
                        bg=color,
                        fg=theme.colors.white,
                        font=theme.font(theme.base_font_size, bold=True),
                        command=lambda p=platform, c=city, w=response.current_weather: execute_share(
                            ctx, c, p, weather=w
                        ),
                    ).pack(side=tk.LEFT, padx=4)

            query_entry.delete(0, tk.END)

        tk.Button(
            frame,
            text="Ask Joyuci",
            command=submit,
            bg="#7E57C2",
            fg=theme.colors.white,
            font=theme.font(theme.large_font_size, bold=True),
            width=15,
        ).pack(pady=10)
        query_entry.bind("<Return>", lambda _e: submit())

        create_back_button(
            frame,
            lambda: MainMenuView(ctx).show(),
            theme=theme,
            images=ctx.image_registry,
            sfx_player=ctx.sfx_player,
            placement=BackButtonPlacement.TOP_LEFT,
        )
