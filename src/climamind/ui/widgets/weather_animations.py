"""Condition-based weather canvas animations."""

from __future__ import annotations

import random
from pathlib import Path
from typing import Any, Mapping

import tkinter as tk
from PIL import Image, ImageTk

from climamind.config.paths import IMAGE_FOLDER
from climamind.domain.models.weather import CurrentWeather
from climamind.ui.theme import UiTheme


class WeatherAnimation:
    """
    Rain, snow, or sunny GIF on a canvas (mirrors ``add_weather_animations``).

    Attach to a parent frame; call ``stop()`` on view leave.
    """

    def __init__(
        self,
        parent: tk.Misc,
        theme: UiTheme | None = None,
        image_folder: Path | None = None,
    ) -> None:
        self._theme = theme or UiTheme()
        self._image_folder = image_folder or IMAGE_FOLDER
        self._canvas = tk.Canvas(
            parent,
            bg=self._theme.default_window_bg,
            height=150,
            highlightthickness=0,
        )
        self._canvas.pack(fill="x", pady=10)
        self._after_id: str | None = None
        self._running = False
        self._gif_frames: list[tk.PhotoImage] = []

    @property
    def canvas(self) -> tk.Canvas:
        return self._canvas

    def start(self, weather_data: CurrentWeather | Mapping[str, Any] | None) -> None:
        self.stop()
        if not weather_data:
            return

        if isinstance(weather_data, CurrentWeather):
            main_cond = weather_data.main.lower()
            temp = weather_data.temp
        else:
            main_cond = str(weather_data.get("main", "")).lower()
            temp = weather_data.get("temp", float("inf"))

        if main_cond in ("rain", "drizzle"):
            self._running = True
            self._animate_rain()
        elif main_cond == "snow" or (isinstance(temp, (int, float)) and temp <= 0):
            self._running = True
            self._animate_snow()
        elif main_cond == "clear":
            self._start_sunny()

    def stop(self) -> None:
        self._running = False
        if self._after_id is not None:
            try:
                self._canvas.after_cancel(self._after_id)
            except tk.TclError:
                pass
            self._after_id = None
        try:
            self._canvas.delete("all")
        except tk.TclError:
            pass
        self._gif_frames.clear()

    def _animate_rain(self) -> None:
        if not self._running:
            return
        self._canvas.delete("raindrop")
        width = max(self._canvas.winfo_width(), 1)
        for _ in range(20):
            x = random.randint(0, width)
            y = random.randint(0, 100)
            self._canvas.create_line(
                x, y, x, y + 5, fill="blue", tags="raindrop"
            )
        self._after_id = self._canvas.after(100, self._animate_rain)

    def _animate_snow(self) -> None:
        if not self._running:
            return
        self._canvas.delete("snowflake")
        width = max(self._canvas.winfo_width(), 1)
        for _ in range(25):
            x = random.randint(0, width)
            y = random.randint(0, 150)
            size = random.randint(4, 6)
            self._canvas.create_oval(
                x - size,
                y - size,
                x + size,
                y + size,
                fill="white",
                outline="#B0BEC5",
                width=1,
                tags="snowflake",
            )
            self._canvas.create_oval(
                x - size + 1,
                y - size + 1,
                x + size + 1,
                y + size + 1,
                fill="#E0E0E0",
                outline="",
                tags="snowflake",
            )
        self._canvas.move("snowflake", 0, 5)
        for snowflake in self._canvas.find_withtag("snowflake"):
            _x1, y1, _x2, y2 = self._canvas.coords(snowflake)
            if y2 > 150:
                self._canvas.delete(snowflake)
        self._after_id = self._canvas.after(120, self._animate_snow)

    def _start_sunny(self) -> None:
        gif_path = self._image_folder / "sunny.gif"
        try:
            gif = Image.open(gif_path)
            frames: list[tk.PhotoImage] = []
            while True:
                frame = gif.copy()
                frame = frame.resize((100, 100), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(frame)
                frames.append(photo)
                gif.seek(len(frames))
        except EOFError:
            pass
        except Exception as exc:
            print(f"GIF yükleme hatası: {exc}")
            self._canvas.create_oval(50, 25, 100, 75, fill="yellow", outline="orange")
            return

        if frames:
            self._gif_frames = frames
            self._running = True
            self._animate_gif(frames, 0)
        else:
            self._canvas.create_oval(50, 25, 100, 75, fill="yellow", outline="orange")

    def _animate_gif(self, frames: list[tk.PhotoImage], index: int) -> None:
        if not self._running or not frames:
            return
        frame = frames[index]
        self._canvas.delete("gif")
        self._canvas.create_image(75, 25, image=frame, anchor="nw", tags="gif")
        next_index = (index + 1) % len(frames)
        self._after_id = self._canvas.after(100, self._animate_gif, frames, next_index)


class MusicRainAnimation:
    """
    Full-screen rain effect for the music page (mirrors ``animate_rain`` on music canvas).

    Requires fog/drop images from ``ImageRegistry``.
    """

    def __init__(
        self,
        canvas: tk.Canvas,
        root: tk.Tk,
        fog_image: tk.PhotoImage | None,
        drop_image: tk.PhotoImage | None,
    ) -> None:
        self._canvas = canvas
        self._root = root
        self._fog_image = fog_image
        self._drop_image = drop_image
        self._object_ids: list[int] = []
        self._loop_after_id: str | None = None
        self._running = False

    def start(self) -> None:
        if self._fog_image is None or self._drop_image is None:
            return
        self._running = True
        self._loop()

    def stop(self) -> None:
        self._running = False
        if self._loop_after_id is not None:
            try:
                self._canvas.after_cancel(self._loop_after_id)
            except tk.TclError:
                pass
            self._loop_after_id = None
        for obj_id in self._object_ids:
            try:
                self._canvas.delete(obj_id)
            except tk.TclError:
                pass
        self._object_ids.clear()

    def _loop(self) -> None:
        if not self._running:
            return

        if not self._object_ids:
            window_width = max(self._root.winfo_width(), 800)
            num_clouds = max(8, window_width // 100)
            for i in range(num_clouds):
                cloud_id = self._canvas.create_image(
                    i * 100 + 50, 50, image=self._fog_image
                )
                self._object_ids.append(cloud_id)

        if self._object_ids:
            for _ in range(3):
                cloud_index = random.randint(0, len(self._object_ids) - 1)
                x = cloud_index * 100 + 50 + random.uniform(-50, 50)
                y = 100
                drop_id = self._canvas.create_image(x, y, image=self._drop_image)
                self._object_ids.append(drop_id)
                self._schedule_drop(drop_id)

        self._loop_after_id = self._canvas.after(25, self._loop)

    def _schedule_drop(self, drop_id: int) -> None:
        def update_drop() -> None:
            if not self._running:
                return
            try:
                if drop_id in self._canvas.find_all():
                    self._canvas.move(drop_id, random.uniform(-2, 2), 10)
                    coords = self._canvas.coords(drop_id)
                    if coords and coords[1] > self._root.winfo_height():
                        self._canvas.delete(drop_id)
                        if drop_id in self._object_ids:
                            self._object_ids.remove(drop_id)
                    else:
                        self._canvas.after(50, update_drop)
                else:
                    if drop_id in self._object_ids:
                        self._object_ids.remove(drop_id)
            except tk.TclError:
                if drop_id in self._object_ids:
                    self._object_ids.remove(drop_id)

        self._canvas.after(50, update_drop)
