"""Natural-language intent parsing for Joyuci queries."""

import re
import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class ParsedQuery:
    """Result of parsing a user question."""

    feature: str | None
    city: str | None

    @property
    def is_valid(self) -> bool:
        return bool(self.feature and self.city)


class QueryParser:
    """Regex-based intent detection (mirrors ``parse_user_query`` in maincode.py)."""

    FEATURE_WEEKLY = "weekly_forecast"
    FEATURE_DANGEROUS = "dangerous_conditions"
    FEATURE_ACTIVITY = "activity_recommendations"

    def parse(self, query: str) -> ParsedQuery:
        query = unicodedata.normalize("NFC", query.strip())
        city_match = re.search(r"\b(in|for)\s+(.+?)(?:\s|$)", query, re.UNICODE)
        city = city_match.group(2).strip() if city_match else None
        if city:
            print(f"DEBUG: Extracted city as entered: {city}")

        query_lower = query.lower()
        feature: str | None = None

        if re.search(r"\b(weekly|week|forecast|5\s*day)\b", query_lower):
            if city:
                feature = self.FEATURE_WEEKLY
        elif re.search(
            r"\b(danger|dangerous|rain|snow|storm|hot|heat)\b", query_lower
        ):
            if city:
                feature = self.FEATURE_DANGEROUS
        elif re.search(
            r"\b(activity|activities|what\s*to\s*do|recommend)\b", query_lower
        ):
            if city:
                feature = self.FEATURE_ACTIVITY

        return ParsedQuery(feature=feature, city=city)
