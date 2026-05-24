"""Chat history DTOs for the Joyuci assistant."""

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass
class ChatEntry:
    """A single user ↔ Joyuci exchange."""

    query: str
    response: str

    def to_dict(self) -> dict[str, str]:
        return {"query": self.query, "response": self.response}

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ChatEntry":
        return cls(
            query=str(data.get("query", "")),
            response=str(data.get("response", "")),
        )
