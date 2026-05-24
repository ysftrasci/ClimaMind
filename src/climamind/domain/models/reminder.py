"""Reminder settings DTO."""

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass
class ReminderSettings:
    """Scheduled weather email reminder for a user."""

    time: str = ""
    city: str = ""
    frequency: str = ""
    custom_days: list[str] = field(default_factory=list)

    def is_complete(self) -> bool:
        return bool(self.time and self.city and self.frequency)

    def to_dict(self) -> dict[str, Any]:
        if not self.time and not self.city and not self.frequency and not self.custom_days:
            return {}
        return {
            "time": self.time,
            "city": self.city,
            "frequency": self.frequency,
            "custom_days": list(self.custom_days),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any] | None) -> "ReminderSettings":
        if not data:
            return cls()
        return cls(
            time=str(data.get("time", "")),
            city=str(data.get("city", "")),
            frequency=str(data.get("frequency", "")),
            custom_days=list(data.get("custom_days", [])),
        )
