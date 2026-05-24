"""Nature ambience playback via Pygame music stream (no Tkinter)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pygame
from mutagen.mp3 import MP3

from climamind.config.paths import MUSIC_FOLDER
from climamind.infrastructure.audio.sfx_player import SfxPlayer


class MusicPlaybackError(Exception):
    """Base class for music playback failures."""


class MusicUnavailableError(MusicPlaybackError):
    """Pygame mixer is not available."""


class MusicFileNotFoundError(MusicPlaybackError):
    """MP3 file for the requested track is missing."""


@dataclass
class MusicPlayResult:
    """Outcome of starting a track."""

    track_name: str
    duration_sec: int
    file_path: Path


class MusicPlayer:
    """
    Manages playlist playback state (mirrors music globals in maincode.py).

    UI widgets (progress bar, labels) bind to this state in a later step.
    """

    AVAILABLE_TRACKS: tuple[str, ...] = (
        "Forest Sounds",
        "Ocean Waves",
        "Rain Ambience",
        "Calm Wind",
        "Birds Chirping",
        "White Noise",
    )

    def __init__(
        self,
        music_folder: Path | None = None,
        *,
        sfx_player: SfxPlayer | None = None,
        available: bool | None = None,
    ) -> None:
        self._music_folder = music_folder or MUSIC_FOLDER
        if available is not None:
            self._available = available
        elif sfx_player is not None:
            self._available = sfx_player.is_available
        else:
            self._available = SfxPlayer().is_available

        self.current_track: str | None = None
        self.played_history: list[str] = []
        self.paused: bool = False
        self.duration_sec: int = 0
        self.last_seek_position_sec: float = 0.0
        self.page_active: bool = False
        self.manually_seeking: bool = False

    @classmethod
    def create(cls, sfx_player: SfxPlayer | None = None) -> MusicPlayer:
        """Factory that reuses mixer availability from ``SfxPlayer`` when provided."""
        return cls(sfx_player=sfx_player)

    @property
    def is_available(self) -> bool:
        return self._available

    @staticmethod
    def format_time(seconds: float) -> str:
        total = int(seconds)
        minutes, secs = divmod(total, 60)
        return f"{minutes}:{secs:02d}"

    def music_file_path(self, music_name: str) -> Path:
        safe = "".join(c for c in music_name if c.isalnum() or c in (" ", "_")).rstrip()
        filename = f"{safe.lower().replace(' ', '_')}.mp3"
        return self._music_folder / filename

    def play(self, music_name: str) -> MusicPlayResult:
        """Load and play *music_name* once (no loop)."""
        print(f"DEBUG: play_music called for {music_name}")
        if not self._available:
            raise MusicUnavailableError("Music playback is not available.")

        self.stop_stream()

        file_path = self.music_file_path(music_name)
        if not file_path.exists():
            print(f"DEBUG: Music file not found: {file_path}")
            raise MusicFileNotFoundError(f"Music file not found: {file_path}")

        try:
            pygame.mixer.music.load(str(file_path))
            pygame.mixer.music.play(0)
            self.current_track = music_name
            if not self.played_history or self.played_history[-1] != music_name:
                self.played_history.append(music_name)
            self.paused = False
            self.last_seek_position_sec = 0.0

            try:
                audio = MP3(str(file_path))
                self.duration_sec = int(audio.info.length)
            except Exception as exc:
                print(f"DEBUG: Müzik süresi alınamadı: {exc}")
                self.duration_sec = 0

            return MusicPlayResult(
                track_name=music_name,
                duration_sec=self.duration_sec,
                file_path=file_path,
            )
        except pygame.error as exc:
            self._reset_state()
            raise MusicPlaybackError(
                f"Error loading or playing '{music_name}': {exc}"
            ) from exc

    def stop(self) -> None:
        """Stop playback and reset state (mirrors ``stop_music`` without widget updates)."""
        print("DEBUG: stop_music called")
        self.stop_stream()
        self._reset_state()
        print("Music stopped.")

    def stop_stream(self) -> None:
        if not self._available:
            return
        try:
            pygame.mixer.music.stop()
            print("DEBUG: Pygame music stopped.")
        except pygame.error as exc:
            print(f"DEBUG: Error stopping music: {exc}")

    def toggle_pause(self) -> bool:
        """Pause or unpause. Returns new paused state."""
        if not self._available or not self.current_track:
            return self.paused
        try:
            if not self.paused:
                pygame.mixer.music.pause()
                self.paused = True
                print("Müzik duraklatıldı.")
            else:
                pygame.mixer.music.unpause()
                self.paused = False
                print("Müzik devam ediyor.")
        except pygame.error as exc:
            print(f"Müzik duraklatma/devam hatası: {exc}")
        return self.paused

    def play_previous(self) -> MusicPlayResult | None:
        if not self._available:
            raise MusicUnavailableError("Music playback is not available.")
        if len(self.played_history) > 1:
            self.played_history.pop()
            if self.played_history:
                previous = self.played_history.pop()
                return self.play(previous)
        return None

    def play_next(self) -> MusicPlayResult | None:
        if not self._available:
            raise MusicUnavailableError("Music playback is not available.")
        if not self.AVAILABLE_TRACKS:
            return None
        if self.current_track:
            try:
                index = self.AVAILABLE_TRACKS.index(self.current_track)
                next_track = self.AVAILABLE_TRACKS[(index + 1) % len(self.AVAILABLE_TRACKS)]
            except ValueError:
                next_track = self.AVAILABLE_TRACKS[0]
        else:
            next_track = self.AVAILABLE_TRACKS[0]
        return self.play(next_track)

    def seek(self, position_sec: float) -> None:
        """Seek within the current track (seconds)."""
        if not self._available or self.duration_sec <= 0:
            return
        position_sec = max(0.0, min(position_sec, max(self.duration_sec - 0.1, 0.0)))
        if pygame.mixer.music.get_busy() or self.paused:
            pygame.mixer.music.set_pos(position_sec)
            self.last_seek_position_sec = position_sec

    def set_volume(self, volume: float) -> None:
        """Set music volume (0.0–1.0)."""
        if not self._available:
            return
        try:
            pygame.mixer.music.set_volume(max(0.0, min(volume, 1.0)))
        except Exception as exc:
            print(f"Ses ayarlanırken hata: {exc}")

    def get_volume(self) -> float:
        if not self._available:
            return 0.0
        try:
            return float(pygame.mixer.music.get_volume())
        except Exception:
            return 0.0

    def is_busy(self) -> bool:
        if not self._available:
            return False
        try:
            return bool(pygame.mixer.music.get_busy())
        except pygame.error:
            return False

    def current_position_sec(self) -> float:
        """Estimated playback position in seconds."""
        if not self._available or self.duration_sec <= 0:
            return 0.0
        pos_ms = pygame.mixer.music.get_pos()
        if pos_ms < 0:
            return self.last_seek_position_sec
        total = self.last_seek_position_sec + pos_ms / 1000.0
        return min(total, float(self.duration_sec))

    def progress_percentage(self) -> float:
        if self.duration_sec <= 0:
            return 0.0
        return (self.current_position_sec() / self.duration_sec) * 100.0

    def tick(self) -> str | None:
        """
        Call periodically from the UI loop when ``page_active`` is True.

        Returns the name of the next track if playback finished and should advance.
        """
        if not self.page_active or not self._available:
            return None
        if self.is_busy() or self.paused:
            return None
        if self.current_track:
            print("DEBUG: Music finished, advancing to next track")
            return self.current_track
        return None

    def _reset_state(self) -> None:
        self.current_track = None
        self.paused = False
        self.duration_sec = 0
        self.last_seek_position_sec = 0.0
