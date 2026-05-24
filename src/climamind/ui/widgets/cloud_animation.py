"""Drifting cloud animation on a Tk canvas."""

from __future__ import annotations

import random
from dataclasses import dataclass

import tkinter as tk


@dataclass
class CloudAnimationConfig:
    """Tunable parameters for cloud drift."""

    count: int = 10
    speed_min: float = 0.5
    speed_max: float = 2.0
    y_min: int = 50
    y_max_ratio: float = 0.7
    interval_ms: int = 50


class CloudAnimation:
    """
    Animates cloud images across a canvas (login, register, search, etc.).

    Call ``stop()`` from the view's navigation ``on_leave`` callback.
    """

    def __init__(
        self,
        canvas: tk.Canvas,
        root: tk.Tk,
        cloud_image: tk.PhotoImage,
        config: CloudAnimationConfig | None = None,
    ) -> None:
        self._canvas = canvas
        self._root = root
        self._cloud_image = cloud_image
        self._config = config or CloudAnimationConfig()
        self._clouds: list[dict] = []
        self._after_id: str | None = None
        self._running = False

    @property
    def is_running(self) -> bool:
        return self._running

    def start(self) -> None:
        if self._running:
            return
        cfg = self._config
        screen_width = self._root.winfo_screenwidth()
        screen_height = self._root.winfo_screenheight()
        y_max = int(screen_height * cfg.y_max_ratio)

        self._clouds = []
        for _ in range(cfg.count):
            self._clouds.append(
                {
                    "x": random.randint(-100, screen_width),
                    "y": random.randint(cfg.y_min, y_max),
                    "speed": random.uniform(cfg.speed_min, cfg.speed_max),
                    "image": self._cloud_image,
                }
            )
        self._running = True
        self._tick()

    def stop(self) -> None:
        self._running = False
        if self._after_id is not None:
            try:
                self._canvas.after_cancel(self._after_id)
            except tk.TclError:
                pass
            self._after_id = None
        try:
            self._canvas.delete("cloud")
        except tk.TclError:
            pass
        self._clouds.clear()

    def _tick(self) -> None:
        if not self._running:
            return

        self._canvas.delete("cloud")
        screen_width = self._root.winfo_screenwidth()
        screen_height = self._root.winfo_screenheight()
        y_max = int(screen_height * self._config.y_max_ratio)

        for cloud in self._clouds:
            x, y, speed = cloud["x"], cloud["y"], cloud["speed"]
            self._canvas.create_image(
                x, y, image=cloud["image"], anchor="nw", tags="cloud"
            )
            cloud["x"] += speed
            if cloud["x"] > screen_width:
                cloud["x"] = -cloud["image"].width()
                cloud["y"] = random.randint(self._config.y_min, y_max)

        self._after_id = self._canvas.after(self._config.interval_ms, self._tick)


def start_cloud_animation(
    canvas: tk.Canvas,
    root: tk.Tk,
    cloud_image: tk.PhotoImage | None,
    *,
    config: CloudAnimationConfig | None = None,
) -> CloudAnimation | None:
    """
    Convenience helper: start animation or log and return None if image missing.

    Returns the controller so the view can pass ``animation.stop`` to ``on_leave``.
    """
    if cloud_image is None:
        print("Cloud animation error: cloud image not loaded")
        return None
    animation = CloudAnimation(canvas, root, cloud_image, config)
    try:
        animation.start()
    except Exception as exc:
        print(f"Cloud animation error: {exc}")
        return None
    return animation
