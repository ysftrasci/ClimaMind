"""Shared UI helpers for auth-style screens."""

from __future__ import annotations

import copy
import tkinter as tk
from pathlib import Path

from PIL import Image, ImageTk

from climamind.config.paths import IMAGE_FOLDER
from climamind.ui.assets.image_registry import ImageRegistry
from climamind.ui.theme import UiTheme
from climamind.ui.widgets.cloud_animation import CloudAnimation, CloudAnimationConfig, start_cloud_animation


def create_welcome_frame(
    parent: tk.Misc,
    title_text: str,
    message_text: str,
    theme: UiTheme | None = None,
) -> tk.Frame:
    """Mirrors ``create_welcome_frame`` from maincode.py."""
    theme = theme or UiTheme()
    c = theme.colors
    welcome_frame = tk.Frame(parent, bg=c.bg_welcome, bd=2, relief=tk.GROOVE, padx=20, pady=20)
    tk.Label(
        welcome_frame,
        text=title_text,
        font=theme.font(theme.welcome_title_font_size, bold=True),
        bg=c.bg_welcome,
        fg=c.fg_primary,
    ).pack(pady=(0, 5))
    tk.Label(
        welcome_frame,
        text=message_text,
        font=theme.font(theme.welcome_message_font_size, italic=True),
        bg=c.bg_welcome,
        justify=tk.CENTER,
    ).pack()
    return welcome_frame


def load_eye_icons(root: tk.Misc, image_folder: Path | None = None) -> tuple[tk.PhotoImage, tk.PhotoImage]:
    folder = image_folder or IMAGE_FOLDER
    try:
        eye_image = Image.open(folder / "eye.png").resize((24, 24), Image.Resampling.LANCZOS)
        eye_icon = ImageTk.PhotoImage(eye_image, master=root)
        eye_off_image = Image.open(folder / "eye_off.png").resize((24, 24), Image.Resampling.LANCZOS)
        eye_off_icon = ImageTk.PhotoImage(eye_off_image, master=root)
        return eye_icon, eye_off_icon
    except Exception as exc:
        print(f"Eye icon load error: {exc}")
        return tk.PhotoImage(master=root), tk.PhotoImage(master=root)


def build_fullscreen_canvas(
    root: tk.Tk,
    theme: UiTheme,
    images: ImageRegistry,
    *,
    cloud_count: int = 10,
    y_max_ratio: float = 0.7,
    speed_min: float = 0.5,
    speed_max: float = 2.0,
) -> tuple[tk.Canvas, CloudAnimation | None]:
    """Create a root-filling canvas with optional cloud animation."""
    canvas = tk.Canvas(
        root,
        bg=theme.default_window_bg,
        highlightthickness=0,
    )
    canvas.pack(fill="both", expand=True)
    cloud_anim = start_cloud_animation(
        canvas,
        root,
        images.get("clouds"),
        config=CloudAnimationConfig(
            count=cloud_count,
            y_max_ratio=y_max_ratio,
            speed_min=speed_min,
            speed_max=speed_max,
        ),
    )
    return canvas, cloud_anim


def panel_bg(theme: UiTheme) -> str:
    return theme.colors.bg_panel


def entry_style_copy(theme: UiTheme, **overrides) -> dict:
    style = copy.deepcopy(theme.large_entry_style())
    style.update(overrides)
    return style
