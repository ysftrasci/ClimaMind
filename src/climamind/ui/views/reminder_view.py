"""Weather reminder configuration screen."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from climamind.config.settings import DAYS_OF_WEEK_EN
from climamind.context import AppContext
from climamind.infrastructure.scheduling.reminder_scheduler import ReminderSchedulingError
from climamind.services.reminder_service import ReminderValidationError
from climamind.ui.views.auth_guard import require_email
from climamind.ui.views.helpers import create_welcome_frame, entry_style_copy, panel_bg
from climamind.ui.views.main_menu_view import MainMenuView
from climamind.ui.widgets.back_button import BackButtonPlacement, create_back_button
from climamind.ui.widgets.cloud_animation import CloudAnimationConfig, start_cloud_animation


class ReminderView:
    def __init__(self, ctx: AppContext) -> None:
        self._ctx = ctx
        self._cloud_anim = None

    def show(self) -> None:
        if not require_email(self._ctx, lambda: MainMenuView(self._ctx).show()):
            return
        if self._ctx.music_player.current_track:
            self._ctx.music_player.stop()
        self._ctx.music_player.page_active = False
        self._ctx.navigation.navigate(
            self._build,
            view_name="reminder",
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
        email = ctx.session_manager.email or ""
        panel = panel_bg(theme)
        bg = theme.default_window_bg

        outer = tk.Frame(root, bg=bg)
        outer.pack(fill="both", expand=True, padx=20, pady=20)

        canvas = tk.Canvas(outer, bg=bg, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        self._cloud_anim = start_cloud_animation(
            canvas,
            root,
            ctx.image_registry.get("clouds"),
            config=CloudAnimationConfig(count=6),
        )

        create_welcome_frame(
            canvas,
            "Set Weather Reminder",
            "Choose when and where to receive your daily weather email.",
            theme,
        ).place(relx=0.5, rely=0.08, anchor="n")

        container = tk.Frame(canvas, bg=panel, bd=2, relief=tk.GROOVE, padx=25, pady=25)
        container.place(relx=0.5, rely=0.45, anchor="center")

        icon_row = tk.Frame(container, bg=panel)
        icon_row.pack(pady=10)
        for key in ("clouds", "umbrella", "snowy"):
            tk.Label(icon_row, image=ctx.image_registry.get(key), bg=panel).pack(
                side=tk.LEFT, padx=10
            )

        form = tk.Frame(container, bg=panel)
        form.pack()

        tk.Label(
            form,
            text="Time (HH:MM):",
            font=theme.font(theme.base_font_size + 2, bold=True),
            bg=panel,
        ).grid(row=0, column=0, sticky="w", pady=8)
        time_entry = tk.Entry(form, **entry_style_copy(theme), width=12)
        time_entry.grid(row=0, column=1, sticky="w", pady=8)

        tk.Label(
            form,
            text="City:",
            font=theme.font(theme.base_font_size + 2, bold=True),
            bg=panel,
        ).grid(row=1, column=0, sticky="w", pady=8)
        city_entry = tk.Entry(form, **entry_style_copy(theme), width=30)
        city_entry.grid(row=1, column=1, sticky="w", pady=8)

        frequency_var = tk.StringVar(value="every_day")
        freq_frame = tk.Frame(form, bg=panel)
        freq_frame.grid(row=2, column=0, columnspan=2, pady=10)
        for text, value in [
            ("Every day", "every_day"),
            ("Weekdays (Mon-Fri)", "weekdays"),
            ("Weekends (Sat-Sun)", "weekends"),
            ("Let me choose...", "custom"),
        ]:
            ttk.Radiobutton(
                freq_frame,
                text=text,
                variable=frequency_var,
                value=value,
            ).pack(anchor="w", padx=10, pady=2)

        custom_frame = tk.Frame(form, bg="#E1F5FE", bd=2, relief=tk.SUNKEN)
        day_vars = {day: tk.BooleanVar() for day in DAYS_OF_WEEK_EN}
        days_inner = tk.Frame(custom_frame, bg="#E1F5FE")
        days_inner.pack(padx=10, pady=10)
        tk.Label(
            days_inner,
            text="Select days:",
            font=theme.font(theme.base_font_size + 1, bold=True),
            bg="#E1F5FE",
        ).pack(anchor="w")
        days_row = tk.Frame(days_inner, bg="#E1F5FE")
        days_row.pack()
        for day in DAYS_OF_WEEK_EN:
            tk.Checkbutton(
                days_row,
                text=day,
                variable=day_vars[day],
                bg="#E1F5FE",
                font=theme.font(theme.base_font_size),
            ).pack(side=tk.LEFT, padx=4)

        def update_custom(*_args: object) -> None:
            if frequency_var.get() == "custom":
                custom_frame.grid(row=3, column=0, columnspan=2, pady=10)
            else:
                custom_frame.grid_remove()

        frequency_var.trace_add("write", update_custom)

        def load_settings() -> None:
            settings = ctx.reminder_service.get_reminder_settings(email)
            time_entry.delete(0, tk.END)
            time_entry.insert(0, settings.time or "08:00")
            city_entry.delete(0, tk.END)
            city_entry.insert(0, settings.city or "")
            frequency_var.set(settings.frequency or "every_day")
            for day in DAYS_OF_WEEK_EN:
                day_vars[day].set(day in settings.custom_days)
            update_custom()

        def save_reminder() -> None:
            ctx.sfx_player.play_click()
            custom_days = [d for d, var in day_vars.items() if var.get()]
            try:
                ctx.reminder_service.save_reminder_from_form(
                    email,
                    time_entry.get(),
                    city_entry.get(),
                    frequency_var.get(),
                    custom_days,
                )
                messagebox.showinfo("Success", "Reminder settings saved successfully!")
                MainMenuView(ctx).show()
            except ReminderValidationError as exc:
                messagebox.showerror("Error", str(exc))
            except ReminderSchedulingError as exc:
                messagebox.showerror("Error", str(exc))

        def clear_reminder() -> None:
            if messagebox.askyesno("Clear Reminder", "Remove your scheduled reminder?"):
                ctx.sfx_player.play_click()
                ctx.reminder_service.clear_reminder(email)
                messagebox.showinfo("Cleared", "Reminder removed.")
                load_settings()

        btn_row = tk.Frame(container, bg=panel)
        btn_row.pack(pady=15)
        tk.Button(
            btn_row,
            text="Save Reminder",
            bg=theme.colors.btn_green,
            fg=theme.colors.white,
            font=theme.font(theme.base_font_size + 1, bold=True),
            command=save_reminder,
        ).pack(side=tk.LEFT, padx=10)
        tk.Button(
            btn_row,
            text="Clear Reminder",
            bg=theme.colors.btn_back,
            fg=theme.colors.white,
            font=theme.font(theme.base_font_size + 1, bold=True),
            command=clear_reminder,
        ).pack(side=tk.LEFT, padx=10)

        load_settings()

        create_back_button(
            outer,
            lambda: MainMenuView(ctx).show(),
            theme=theme,
            images=ctx.image_registry,
            sfx_player=ctx.sfx_player,
            placement=BackButtonPlacement.BOTTOM_CENTER,
        )
