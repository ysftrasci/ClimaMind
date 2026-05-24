"""JSON file persistence for user accounts."""

import json
import os
from pathlib import Path
from typing import Callable

from climamind.config.paths import USERS_FILE
from climamind.domain.models.user import User


class UserRepository:
    """Loads and saves users from ``users.json`` (same format as maincode.py)."""

    def __init__(
        self,
        users_file: Path | str | None = None,
        on_read_error: Callable[[str], None] | None = None,
        on_save_error: Callable[[str], None] | None = None,
    ) -> None:
        self._users_file = Path(users_file) if users_file else USERS_FILE
        self._on_read_error = on_read_error
        self._on_save_error = on_save_error

    @property
    def users_file(self) -> Path:
        return self._users_file

    def load_all(self) -> dict[str, User]:
        """
        Read all users from disk.

        Mirrors ``load_users()`` in maincode.py: ensures ``chat_history`` exists,
        renames corrupted files, returns an empty dict on failure.
        """
        path = self._users_file
        try:
            if not path.exists():
                return {}
            content = path.read_text(encoding="utf-8")
            if not content:
                return {}
            raw = json.loads(content)
            users: dict[str, User] = {}
            for email, data in raw.items():
                if not isinstance(data, dict):
                    continue
                data.setdefault("chat_history", [])
                users[email] = User.from_dict(data)
            return users
        except (FileNotFoundError, json.JSONDecodeError) as exc:
            message = f"Could not read user data ({exc}). A new data file will be created."
            print(f"❌ Error reading user file ({path}): {exc}")
            self._notify_read_error(message)
            self._rename_corrupted(path)
            return {}
        except Exception as exc:
            print(f"❌ Unexpected user loading error: {exc}")
            return {}

    def save_all(self, users: dict[str, User]) -> bool:
        """
        Persist all users to disk.

        Mirrors ``save_users()`` in maincode.py. Returns True on success.
        """
        path = self._users_file
        try:
            payload = {email: user.to_dict() for email, user in users.items()}
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w", encoding="utf-8") as file:
                json.dump(payload, file, indent=4, ensure_ascii=False)
            return True
        except Exception as exc:
            print(f"❌ Error saving user file ({path}): {exc}")
            self._notify_save_error("Could not save user data.")
            return False

    def _notify_read_error(self, message: str) -> None:
        if self._on_read_error:
            self._on_read_error(message)

    def _notify_save_error(self, message: str) -> None:
        if self._on_save_error:
            self._on_save_error(message)

    @staticmethod
    def _rename_corrupted(path: Path) -> None:
        try:
            os.rename(path, str(path) + ".corrupted")
        except OSError:
            pass
