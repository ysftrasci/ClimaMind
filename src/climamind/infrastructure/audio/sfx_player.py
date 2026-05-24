"""Short UI sound effects via Pygame (no Tkinter)."""

from pathlib import Path

import pygame

from climamind.config.paths import SOUNDS_FOLDER


class SfxPlayer:
    """Plays click, success, and error sounds from ``assets/sounds``."""

    def __init__(self, sounds_folder: Path | None = None) -> None:
        self._sounds_folder = Path(sounds_folder) if sounds_folder else SOUNDS_FOLDER
        self._available = self._init_mixer()

    @property
    def is_available(self) -> bool:
        return self._available

    def play_click(self) -> None:
        self._play("click.mp3")

    def play_back_button(self) -> None:
        self._play("back_button.mp3")

    def play_success(self) -> None:
        self._play("success.mp3")

    def play_error(self) -> None:
        self._play("error.mp3")

    def play_register_success(self) -> None:
        self._play("register_success.mp3")

    def play_field_complete(self) -> None:
        self._play("field_complete.mp3")

    def _init_mixer(self) -> bool:
        try:
            pygame.mixer.init()
            return True
        except pygame.error:
            print("⚠️ Pygame mixer could not be initialized. Music features disabled.")
            return False

    def _play(self, filename: str, volume: float = 1.0) -> None:
        if not self._available:
            return
        path = self._sounds_folder / filename
        try:
            sound = pygame.mixer.Sound(str(path))
            sound.set_volume(volume)
            channel = pygame.mixer.find_channel(True)
            if channel:
                channel.play(sound)
        except Exception as exc:
            print(f"Sound error ({filename}): {exc}")
