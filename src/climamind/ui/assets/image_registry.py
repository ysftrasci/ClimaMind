"""Application icon and image loading for Tkinter."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from typing import Any

from PIL import Image, ImageTk

from climamind.config.paths import IMAGE_FOLDER

# (filename, (width, height))
_ICON_SPECS: dict[str, tuple[str, tuple[int, int]]] = {
    "settings": ("setting.png", (40, 40)),
    "password": ("forgot.png", (45, 45)),
    "delete": ("delete.png", (45, 45)),
    "exit": ("exit.png", (40, 40)),
    "logout": ("logout.png", (40, 40)),
    "umbrella": ("umbrella.png", (80, 80)),
    "clouds": ("clouds.png", (100, 100)),
    "contrast": ("contrast.png", (100, 100)),
    "fog": ("fog.png", (100, 100)),
    "snowy": ("snowy.png", (100, 100)),
    "search": ("search.png", (30, 30)),
    "reminder": ("reminder.png", (30, 30)),
    "music": ("music.png", (30, 30)),
    "login": ("login.png", (30, 30)),
    "register": ("register.png", (30, 30)),
    "close": ("close.png", (30, 30)),
    "back_icon": ("back.png", (30, 30)),
    "account_icon": ("account.png", (40, 40)),
    "favourite_icon": ("favourite.png", (40, 40)),
    "previous": ("previous.png", (55, 55)),
    "pause": ("pause.png", (50, 50)),
    "next": ("next.png", (50, 50)),
    "chat_icon": ("chat_icon.png", (30, 30)),
    "forest": ("forest.png", (150, 150)),
    "ocean": ("ocean.png", (150, 150)),
    "rain": ("rain.png", (150, 150)),
    "wind": ("wind1.png", (150, 150)),
    "birds": ("birds.png", (150, 150)),
    "white_noise": ("white.png", (150, 150)),
    "drop": ("drop.png", (20, 20)),
    "clock_icon": ("clock.png", (20, 20)),
    "map_pin_icon": ("map_pin.png", (20, 20)),
}

_LARGE_DEFAULT_KEYS = frozenset({"clouds", "contrast", "fog", "snowy"})
_MEDIUM_DEFAULT_KEYS = frozenset({"umbrella"})


class ImageRegistry:
    """Loads and caches ``PhotoImage`` assets (mirrors global ``images`` in maincode.py)."""

    def __init__(
        self,
        image_folder: Path | None = None,
        master: tk.Misc | None = None,
    ) -> None:
        self._image_folder = Path(image_folder) if image_folder else IMAGE_FOLDER
        self._master = master
        self._images: dict[str, Any] = {}
        self._defaults_created = False

    @property
    def images(self) -> dict[str, Any]:
        """Read-only view of loaded images."""
        return self._images

    def get(self, key: str, default: Any = None) -> Any:
        return self._images.get(key, default)

    def load_all(self, master: tk.Misc | None = None) -> dict[str, Any]:
        """
        Load every configured icon and apply fallbacks for missing files.

        Args:
            master: Tk root/widget required for blank ``PhotoImage`` placeholders.

        Returns:
            The internal images dictionary.
        """
        if master is not None:
            self._master = master

        self._images = {
            key: self._load_image(filename, size)
            for key, (filename, size) in _ICON_SPECS.items()
        }

        if self._images.get("logout") is None and self._images.get("exit") is not None:
            self._images["logout"] = self._images["exit"]
        if self._images.get("close") is None and self._images.get("delete") is not None:
            self._images["close"] = self._images["delete"]

        self._apply_default_placeholders()
        return self._images

    def _load_image(self, filename: str, size: tuple[int, int]) -> ImageTk.PhotoImage | None:
        try:
            path = self._image_folder / filename
            if not path.exists():
                print(f"⚠️ Image file not found: {path}")
                return None
            image = Image.open(path)
            image = image.resize(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(image)
        except Exception as exc:
            print(f"❌ Error loading image ({filename}): {exc}")
            return None

    def _apply_default_placeholders(self) -> None:
        if self._master is None:
            return

        small = tk.PhotoImage(master=self._master, width=30, height=30)
        medium = tk.PhotoImage(master=self._master, width=80, height=80)
        large = tk.PhotoImage(master=self._master, width=100, height=100)

        for key, img in self._images.items():
            if img is not None:
                continue
            print(f"Assigning default icon for '{key}'.")
            if key in _MEDIUM_DEFAULT_KEYS:
                self._images[key] = medium
            elif key in _LARGE_DEFAULT_KEYS:
                self._images[key] = large
            else:
                self._images[key] = small

        self._defaults_created = True
