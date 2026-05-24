"""Filesystem paths for application assets and data."""

from pathlib import Path

# Package: UmbrellaReminder/src/climamind/config/paths.py
_PACKAGE_ROOT = Path(__file__).resolve().parent.parent
_SRC_ROOT = _PACKAGE_ROOT.parent
APP_ROOT = _SRC_ROOT.parent
BASE_DIR = APP_ROOT

MUSIC_FOLDER = BASE_DIR / "Müzikler"
IMAGE_FOLDER = BASE_DIR / "Resimler"
SOUNDS_FOLDER = BASE_DIR / "sounds"
USERS_FILE = BASE_DIR / "users.json"


def ensure_music_folder() -> None:
    """Create the music directory if it does not exist (mirrors maincode.py startup)."""
    if MUSIC_FOLDER.exists():
        return
    try:
        MUSIC_FOLDER.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: '{MUSIC_FOLDER}'")
    except OSError as exc:
        print(f"❌ Could not create directory '{MUSIC_FOLDER}': {exc}")
