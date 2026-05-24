"""User aggregate and nested profile DTOs."""

from dataclasses import dataclass, field
from typing import Any, Mapping

from climamind.domain.models.chat import ChatEntry
from climamind.domain.models.reminder import ReminderSettings


@dataclass
class AccountProfile:
    """Optional profile fields stored under user.account."""

    username: str = ""
    district: str = ""
    profile_picture: str = "No file selected"

    def to_dict(self) -> dict[str, str]:
        if (
            not self.username
            and not self.district
            and self.profile_picture == "No file selected"
        ):
            return {}
        return {
            "username": self.username,
            "district": self.district,
            "profile_picture": self.profile_picture,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any] | None) -> "AccountProfile":
        if not data:
            return cls()
        return cls(
            username=str(data.get("username", "")),
            district=str(data.get("district", "")),
            profile_picture=str(data.get("profile_picture", "No file selected")),
        )


@dataclass
class User:
    """Registered application user (keyed by email in persistence)."""

    password: str = ""
    verified: bool = False
    favorites: list[str] = field(default_factory=list)
    reminder: ReminderSettings = field(default_factory=ReminderSettings)
    account: AccountProfile = field(default_factory=AccountProfile)
    chat_history: list[ChatEntry] = field(default_factory=list)
    reset_code: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "password": self.password,
            "verified": self.verified,
            "favorites": list(self.favorites),
            "reminder": self.reminder.to_dict(),
            "account": self.account.to_dict(),
            "chat_history": [entry.to_dict() for entry in self.chat_history],
        }
        if self.reset_code is not None:
            payload["reset_code"] = self.reset_code
        return payload

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "User":
        return cls(
            password=str(data.get("password", "")),
            verified=bool(data.get("verified", False)),
            favorites=list(data.get("favorites", [])),
            reminder=ReminderSettings.from_dict(data.get("reminder")),
            account=AccountProfile.from_dict(data.get("account")),
            chat_history=[
                ChatEntry.from_dict(entry)
                for entry in data.get("chat_history", [])
            ],
            reset_code=data.get("reset_code"),
        )
