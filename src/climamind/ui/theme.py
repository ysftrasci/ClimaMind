"""Shared fonts, colors, and Tk widget style dictionaries."""

from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass, field


@dataclass(frozen=True)
class UiColors:
    """Background and accent colors used across screens."""

    bg_primary: str = "#E0F7FA"
    bg_panel: str = "#E6F0FA"
    bg_card: str = "#B2EBF2"
    bg_soft_blue: str = "#EDF6FF"
    bg_settings: str = "#E3F2FD"
    bg_welcome: str = "#F3E5F5"
    bg_title_logged_out: str = "#F3E5F5"
    bg_title_logged_in: str = "#ADD8E6"

    fg_primary: str = "#006064"
    fg_secondary: str = "#004D40"
    fg_title: str = "#1A237E"
    fg_body: str = "#212121"
    fg_muted: str = "#424242"
    fg_error: str = "#D32F2F"
    fg_accent_pink: str = "#AD1457"

    white: str = "#FFFFFF"
    btn_green: str = "#4CAF50"
    btn_green_hover: str = "#66BB6A"
    btn_back: str = "#90A4AE"
    btn_back_hover: str = "#B0BEC5"
    btn_blue: str = "#2196F3"
    btn_blue_hover: str = "#42A5F5"
    btn_joyuci: str = "#7E57C2"
    btn_orange: str = "#FF9800"
    btn_teal: str = "#4DB6AC"
    btn_light_green: str = "#81C784"
    btn_gray: str = "#B0BEC5"
    btn_music: str = "#80CBC4"
    border_green: str = "#4CAF50"
    wave_green: str = "#A5D6A7"
    shadow: str = "#78909C"
    particle: str = "#4FC3F7"


@dataclass
class UiTheme:
    """Central theme tokens (mirrors maincode.py style constants)."""

    colors: UiColors = field(default_factory=UiColors)

    font_family: str = "Arial"
    font_family_alt: str = "Helvetica"

    base_font_size: int = 10
    large_font_size: int = 12
    title_font_size: int = 18
    main_title_font_size: int = 24
    welcome_title_font_size: int = 24
    welcome_message_font_size: int = 16

    @property
    def default_window_bg(self) -> str:
        return self.colors.bg_primary

    def font(self, size: int, *, bold: bool = False, italic: bool = False) -> tuple:
        style: list[str] = []
        if bold:
            style.append("bold")
        if italic:
            style.append("italic")
        if style:
            return (self.font_family, size, " ".join(style))
        return (self.font_family, size)

    def large_button_style(self) -> dict:
        return {
            "width": 15,
            "height": 2,
            "bg": self.colors.btn_green,
            "fg": self.colors.white,
            "font": self.font(self.large_font_size, bold=True),
            "relief": tk.RAISED,
            "borderwidth": 2,
        }

    def large_entry_style(self) -> dict:
        return {
            "font": self.font(self.large_font_size),
            "borderwidth": 1,
            "relief": tk.SOLID,
        }

    def main_menu_button_style(self, *, logged_in: bool = True) -> dict:
        height = 40 if logged_in else 50
        return {
            "width": 200,
            "height": height,
            "compound": "left",
            "font": self.font(self.base_font_size + 1, bold=True),
            "padx": 10,
        }

    def settings_button_style(self) -> dict:
        return {
            "width": 15,
            "height": 3,
            "font": self.font(self.base_font_size + 1, bold=True),
        }

    def settings_button_style_large(self) -> dict:
        base = self.settings_button_style()
        return {
            **base,
            "width": 350,
            "compound": "left",
            "padx": 10,
            "height": 70,
            "font": self.font(14, bold=True),
        }


# Module-level default instance for convenience
theme = UiTheme()
