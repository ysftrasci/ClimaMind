"""Favorite cities management screen."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from climamind.context import AppContext
from climamind.services.favorites_service import (
    CityNotInFavoritesError,
    FavoritesError,
    InvalidCityError,
)
from climamind.ui.views.auth_guard import require_email
from climamind.ui.views.helpers import create_welcome_frame, entry_style_copy, panel_bg
from climamind.ui.widgets.back_button import BackButtonPlacement, create_back_button
from climamind.ui.widgets.cloud_animation import CloudAnimationConfig, start_cloud_animation


class FavoritesView:
    def __init__(self, ctx: AppContext) -> None:
        self._ctx = ctx
        self._cloud_anim = None
        self._list_frame: tk.Frame | None = None

    def show(self) -> None:
        if not require_email(self._ctx, self._open_settings):
            return
        self._ctx.navigation.navigate(
            self._build,
            view_name="favorites",
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

        outer = tk.Frame(root, bg=bg)
        outer.pack(fill="both", expand=True, padx=20, pady=20)

        canvas = tk.Canvas(outer, bg=bg, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        self._cloud_anim = start_cloud_animation(
            canvas, root, ctx.image_registry.get("clouds")
        )

        create_welcome_frame(
            canvas,
            "Manage Favorites",
            "Add or remove cities for quick weather search.",
            theme,
        ).place(relx=0.5, rely=0.08, anchor="n")

        container = tk.Frame(canvas, bg=panel, bd=2, relief=tk.GROOVE, padx=20, pady=20)
        container.place(relx=0.5, rely=0.5, anchor="center", width=650, height=380)

        add_row = tk.Frame(container, bg=panel)
        add_row.pack(pady=10, fill="x")
        tk.Label(
            add_row,
            text="Add city:",
            font=theme.font(theme.large_font_size),
            bg=panel,
        ).pack(side=tk.LEFT, padx=5)
        city_entry = tk.Entry(add_row, **entry_style_copy(theme), width=25)
        city_entry.pack(side=tk.LEFT, padx=5)

        self._list_frame = tk.Frame(container, bg=panel)
        self._list_frame.pack(fill="both", expand=True, pady=10)

        def refresh_list() -> None:
            assert self._list_frame is not None
            for w in self._list_frame.winfo_children():
                w.destroy()
            try:
                cities = ctx.favorites_service.list_favorites(email)
            except FavoritesError as exc:
                tk.Label(
                    self._list_frame,
                    text=str(exc),
                    bg=panel,
                    fg="red",
                ).pack()
                return
            if not cities:
                tk.Label(
                    self._list_frame,
                    text="No favorite cities yet.",
                    font=theme.font(theme.large_font_size, italic=True),
                    bg=panel,
                ).pack(pady=20)
                return
            for city in cities:
                row = tk.Frame(self._list_frame, bg=panel)
                row.pack(fill="x", pady=4)
                tk.Label(
                    row,
                    text=city,
                    font=theme.font(theme.base_font_size + 1),
                    bg=panel,
                    width=25,
                    anchor="w",
                ).pack(side=tk.LEFT, padx=10)
                tk.Button(
                    row,
                    text="Remove",
                    bg="#E57373",
                    fg=theme.colors.white,
                    font=theme.font(theme.base_font_size, bold=True),
                    command=lambda c=city: remove_city(c),
                ).pack(side=tk.RIGHT, padx=10)

        def add_city() -> None:
            ctx.sfx_player.play_click()
            try:
                ctx.favorites_service.add_favorite(email, city_entry.get())
                city_entry.delete(0, tk.END)
                messagebox.showinfo("Success", "City added to favorites!")
                refresh_list()
            except (InvalidCityError, FavoritesError) as exc:
                messagebox.showerror("Error", str(exc))

        def remove_city(city: str) -> None:
            ctx.sfx_player.play_click()
            try:
                ctx.favorites_service.remove_favorite(email, city)
                refresh_list()
            except (CityNotInFavoritesError, FavoritesError) as exc:
                messagebox.showerror("Error", str(exc))

        tk.Button(
            add_row,
            text="Add",
            bg="#2196F3",
            fg=theme.colors.white,
            font=theme.font(theme.base_font_size, bold=True),
            command=add_city,
        ).pack(side=tk.LEFT, padx=5)
        city_entry.bind("<Return>", lambda _e: add_city())

        refresh_list()

        create_back_button(
            outer,
            self._open_settings,
            theme=theme,
            images=ctx.image_registry,
            sfx_player=ctx.sfx_player,
            placement=BackButtonPlacement.BOTTOM_CENTER,
        )
