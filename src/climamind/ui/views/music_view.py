"""Nature sounds / music player screen."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from climamind.context import AppContext
from climamind.infrastructure.audio.music_player import (
    MusicFileNotFoundError,
    MusicPlaybackError,
    MusicUnavailableError,
)
from climamind.ui.views.helpers import panel_bg
from climamind.ui.views.main_menu_view import MainMenuView
from climamind.ui.widgets.back_button import BackButtonPlacement, create_back_button
from climamind.ui.widgets.weather_animations import MusicRainAnimation


class MusicView:
    TRACK_ICONS: dict[str, str] = {
        "Forest Sounds": "forest",
        "Ocean Waves": "ocean",
        "Rain Ambience": "rain",
        "Calm Wind": "wind",
        "Birds Chirping": "birds",
        "White Noise": "white_noise",
    }

    def __init__(self, ctx: AppContext) -> None:
        self._ctx = ctx
        self._rain_anim: MusicRainAnimation | None = None
        self._tick_after_id: str | None = None
        self._current_label: tk.Label | None = None
        self._elapsed_label: tk.Label | None = None
        self._progress_scale: tk.Scale | None = None

    def show(self) -> None:
        self._ctx.navigation.navigate(
            self._build,
            view_name="music",
            on_leave=self._cleanup,
        )

    def _cleanup(self) -> None:
        player = self._ctx.music_player
        player.page_active = False
        if self._tick_after_id:
            try:
                self._ctx.root.after_cancel(self._tick_after_id)
            except tk.TclError:
                pass
            self._tick_after_id = None
        if self._rain_anim is not None:
            self._rain_anim.stop()
            self._rain_anim = None

    def _build(self) -> None:
        ctx = self._ctx
        theme = ctx.theme
        root = ctx.root
        player = ctx.music_player
        player.page_active = True
        player.manually_seeking = False

        bg = theme.default_window_bg
        panel = panel_bg(theme)

        frame = tk.Frame(root, bg=bg)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        anim_canvas = tk.Canvas(frame, bg=bg, highlightthickness=0)
        anim_canvas.place(relwidth=1.0, relheight=1.0, relx=0, rely=0)

        self._rain_anim = MusicRainAnimation(
            anim_canvas,
            root,
            ctx.image_registry.get("fog"),
            ctx.image_registry.get("drop"),
        )

        title = tk.Frame(frame, bg=theme.colors.bg_card, bd=2, relief=tk.RAISED)
        title.place(relx=0.5, rely=0.05, anchor="n")
        tk.Label(
            title,
            text="Study with Nature Sounds",
            font=theme.font(theme.main_title_font_size, bold=True),
            bg=theme.colors.bg_card,
            fg="#006064",
        ).pack(padx=10, pady=5)

        buttons_frame = tk.Frame(frame, bg=bg)
        buttons_frame.place(relx=0.5, rely=0.45, anchor="center")

        def play_track(name: str) -> None:
            ctx.sfx_player.play_click()
            try:
                player.play(name)
            except MusicUnavailableError:
                messagebox.showerror("Music", "Music playback is not available.")
                return
            except MusicFileNotFoundError as exc:
                messagebox.showerror("Music", str(exc))
                return
            except MusicPlaybackError as exc:
                messagebox.showerror("Music", str(exc))
                return
            if name == "Rain Ambience":
                self._rain_anim.start()
            else:
                self._rain_anim.stop()
            _refresh_ui()

        col = 0
        tracks = list(player.AVAILABLE_TRACKS)
        for i in range(0, len(tracks), 2):
            col_frame = tk.Frame(buttons_frame, bg=bg)
            col_frame.grid(row=0, column=col, padx=40)
            for track in tracks[i : i + 2]:
                box = tk.Frame(col_frame, bg=bg)
                box.pack(pady=25)
                icon_key = self.TRACK_ICONS.get(track, "forest")
                icon = ctx.image_registry.get(icon_key)
                if icon:
                    tk.Button(
                        box,
                        image=icon,
                        bg=bg,
                        borderwidth=0,
                        command=lambda t=track: play_track(t),
                    ).pack()
                tk.Button(
                    box,
                    text=track,
                    width=15,
                    bg="#80CBC4",
                    fg=theme.colors.white,
                    font=theme.font(theme.base_font_size, bold=True),
                    command=lambda t=track: play_track(t),
                ).pack(pady=5)
            col += 1

        controls = tk.Frame(frame, bg=theme.colors.bg_card, bd=1, relief=tk.GROOVE)
        controls.pack(side="bottom", fill="x", ipady=5)

        inner = tk.Frame(controls, bg=theme.colors.bg_card)
        inner.pack(expand=True, fill="x", padx=10)

        def prev_track() -> None:
            ctx.sfx_player.play_click()
            try:
                result = player.play_previous()
            except MusicUnavailableError:
                return
            if result and result.track_name == "Rain Ambience":
                self._rain_anim.start()
            elif result:
                self._rain_anim.stop()
            _refresh_ui()

        def next_track() -> None:
            ctx.sfx_player.play_click()
            try:
                result = player.play_next()
            except MusicUnavailableError:
                return
            if result and result.track_name == "Rain Ambience":
                self._rain_anim.start()
            elif result:
                self._rain_anim.stop()
            _refresh_ui()

        def toggle_pause() -> None:
            ctx.sfx_player.play_click()
            player.toggle_pause()
            _refresh_ui()

        tk.Button(
            inner,
            image=ctx.image_registry.get("previous"),
            bg=theme.colors.bg_card,
            borderwidth=0,
            command=prev_track,
        ).grid(row=0, column=0, rowspan=2, padx=5)
        tk.Button(
            inner,
            image=ctx.image_registry.get("pause"),
            bg=theme.colors.bg_card,
            borderwidth=0,
            command=toggle_pause,
        ).grid(row=0, column=1, rowspan=2, padx=5)
        tk.Button(
            inner,
            image=ctx.image_registry.get("next"),
            bg=theme.colors.bg_card,
            borderwidth=0,
            command=next_track,
        ).grid(row=0, column=2, rowspan=2, padx=5)

        self._current_label = tk.Label(
            inner,
            text="",
            bg=theme.colors.bg_card,
            font=theme.font(theme.base_font_size + 1, italic=True),
        )
        self._current_label.grid(row=0, column=3, padx=10)

        self._progress_scale = tk.Scale(
            inner,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            showvalue=False,
            bg=theme.colors.bg_card,
            highlightthickness=0,
            troughcolor="#C5CAE9",
        )
        self._progress_scale.grid(row=1, column=3, sticky="ew", padx=10)
        inner.grid_columnconfigure(3, weight=1)

        def on_seek_press(_event: object) -> None:
            player.manually_seeking = True

        def on_seek_release(_event: object) -> None:
            if not player.manually_seeking or player.duration_sec <= 0:
                player.manually_seeking = False
                return
            pct = self._progress_scale.get() if self._progress_scale else 0
            pos = (pct / 100.0) * player.duration_sec
            try:
                player.seek(pos)
            except Exception as exc:
                messagebox.showerror("Seek Error", str(exc))
            player.manually_seeking = False
            _refresh_ui()

        self._progress_scale.bind("<ButtonPress-1>", on_seek_press)
        self._progress_scale.bind("<ButtonRelease-1>", on_seek_release)

        self._elapsed_label = tk.Label(
            inner,
            text="0:00/0:00",
            bg=theme.colors.bg_card,
            font=theme.font(theme.base_font_size),
        )
        self._elapsed_label.grid(row=0, column=4, rowspan=2, padx=5)

        def set_volume(val: str) -> None:
            player.set_volume(float(val) / 100.0)

        vol = tk.Scale(
            inner,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            label="Vol",
            command=set_volume,
            bg=theme.colors.bg_card,
            length=80,
        )
        vol.set(int(player.get_volume() * 100))
        vol.grid(row=0, column=5, rowspan=2, padx=5)

        def _refresh_ui() -> None:
            if self._current_label:
                self._current_label.config(
                    text=player.current_track or ""
                )
            if self._elapsed_label and player.duration_sec > 0:
                pos = player.current_position_sec()
                self._elapsed_label.config(
                    text=f"{player.format_time(pos)}/{player.format_time(player.duration_sec)}"
                )
            elif self._elapsed_label:
                self._elapsed_label.config(text="0:00/0:00")
            if self._progress_scale and not player.manually_seeking:
                self._progress_scale.config(to=100)
                self._progress_scale.set(player.progress_percentage())

        def _tick() -> None:
            if not player.page_active:
                return
            finished = player.tick()
            if finished:
                try:
                    result = player.play_next()
                except MusicUnavailableError:
                    result = None
                if result and result.track_name == "Rain Ambience":
                    self._rain_anim.start()
                else:
                    self._rain_anim.stop()
            _refresh_ui()
            self._tick_after_id = root.after(500, _tick)

        _refresh_ui()
        self._tick_after_id = root.after(500, _tick)

        if player.current_track == "Rain Ambience":
            self._rain_anim.start()

        create_back_button(
            frame,
            lambda: MainMenuView(ctx).show(),
            theme=theme,
            images=ctx.image_registry,
            sfx_player=ctx.sfx_player,
            placement=BackButtonPlacement.BOTTOM_PACKED,
        )
