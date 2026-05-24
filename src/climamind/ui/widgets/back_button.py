"""Reusable back navigation button."""

from __future__ import annotations

from collections.abc import Callable
from enum import Enum

import tkinter as tk

from climamind.infrastructure.audio.sfx_player import SfxPlayer
from climamind.ui.assets.image_registry import ImageRegistry
from climamind.ui.theme import UiTheme


class BackButtonPlacement(Enum):
    """Where the back control is anchored (patterns from maincode.py)."""

    BOTTOM_PACKED = "bottom_packed"
    TOP_LEFT = "top_left"
    BOTTOM_CENTER = "bottom_center"


def create_back_button(
    parent: tk.Misc,
    command: Callable[[], None],
    *,
    theme: UiTheme | None = None,
    images: ImageRegistry | dict | None = None,
    sfx_player: SfxPlayer | None = None,
    placement: BackButtonPlacement = BackButtonPlacement.BOTTOM_PACKED,
    text: str = "Back",
    width: int = 150,
) -> tk.Button:
    """
    Create a back button that plays the back sound then runs *command*.

    Mirrors ``create_back_button`` and alternate ``place`` layouts in maincode.py.
    """
    theme = theme or UiTheme()
    bg = parent.cget("bg") if hasattr(parent, "cget") else theme.default_window_bg

    def on_click() -> None:
        if sfx_player is not None:
            sfx_player.play_back_button()
        command()

    icon = None
    if images is not None:
        if isinstance(images, ImageRegistry):
            icon = images.get("back_icon")
        else:
            icon = images.get("back_icon")

    button_parent: tk.Misc = parent
    if placement == BackButtonPlacement.BOTTOM_PACKED:
        button_parent = tk.Frame(parent, bg=bg)
        button_parent.pack(side="bottom", fill="x", pady=10)

    button = tk.Button(
        button_parent,
        text=text,
        command=on_click,
        width=width,
        bg=theme.colors.btn_back,
        fg=theme.colors.white,
        font=theme.font(theme.base_font_size, bold=True),
        compound="left",
        relief=tk.RAISED,
    )
    if icon is not None:
        button.config(image=icon)

    if placement == BackButtonPlacement.BOTTOM_PACKED:
        button.pack()
    elif placement == BackButtonPlacement.TOP_LEFT:
        button.place(relx=0.0, rely=0.0, anchor="nw", x=10, y=10)
    elif placement == BackButtonPlacement.BOTTOM_CENTER:
        button.bind("<Enter>", lambda e: button.config(bg=theme.colors.btn_back_hover))
        button.bind("<Leave>", lambda e: button.config(bg=theme.colors.btn_back))
        button.place(relx=0.5, rely=0.95, anchor="s")

    return button
