"""Social platform share message and URL building (no UI)."""

from dataclasses import dataclass
from typing import Any, Mapping
from urllib.parse import quote

from climamind.domain.models.weather import CurrentWeather


class UnsupportedPlatformError(Exception):
    """Raised when the platform name is not recognized."""


@dataclass(frozen=True)
class ShareAction:
    """
  Instructions for the UI layer to complete a share.

  The view should copy ``clipboard_text`` when set, open ``browser_url`` when set,
  and optionally show ``user_notice`` in a dialog.
    """

    message: str
    platform: str
    browser_url: str | None = None
    clipboard_text: str | None = None
    user_notice: str | None = None


class SocialShareService:
    """Builds share payloads (mirrors ``share_on_social`` message/URL logic)."""

    HASHTAG = "#ClimaMind"
    LINKEDIN_SHARE_URL = (
        "https://www.linkedin.com/sharing/share-offsite/?url=https://www.climamind.com"
    )
    INSTAGRAM_URL = "https://www.instagram.com"

    def build_share(
        self,
        city: str,
        platform: str,
        content_type: str = "weather",
        weather_data: CurrentWeather | Mapping[str, Any] | None = None,
        recommendations: str | None = None,
    ) -> ShareAction:
        city = city.strip().title()
        message = self._build_message(city, content_type, weather_data, recommendations)
        platform = platform.lower()

        if platform == "instagram":
            return ShareAction(
                message=message,
                platform=platform,
                browser_url=self.INSTAGRAM_URL,
                clipboard_text=message,
                user_notice=(
                    "Message copied to clipboard! Open Instagram, create a story "
                    "or post, and paste the message."
                ),
            )
        if platform == "whatsapp":
            return ShareAction(
                message=message,
                platform=platform,
                browser_url=f"https://api.whatsapp.com/send?text={quote(message)}",
            )
        if platform == "linkedin":
            return ShareAction(
                message=message,
                platform=platform,
                browser_url=self.LINKEDIN_SHARE_URL,
                clipboard_text=message,
                user_notice=(
                    "Message copied to clipboard! Open LinkedIn, create a post, "
                    "and paste the message."
                ),
            )
        if platform == "x":
            return ShareAction(
                message=message,
                platform=platform,
                browser_url=f"https://x.com/intent/tweet?text={quote(message)}",
            )

        raise UnsupportedPlatformError(f"Unsupported platform: {platform}")

    def _build_message(
        self,
        city: str,
        content_type: str,
        weather_data: CurrentWeather | Mapping[str, Any] | None,
        recommendations: str | None,
    ) -> str:
        if content_type == "weather" and weather_data:
            if isinstance(weather_data, CurrentWeather):
                temp = weather_data.temp
                description = weather_data.description.capitalize()
                main_cond = weather_data.main.lower()
            else:
                temp = weather_data.get("temp", "N/A")
                description = str(weather_data.get("description", "N/A")).capitalize()
                main_cond = str(weather_data.get("main", "")).lower()
            emoji = self._weather_emoji(main_cond)
            if isinstance(temp, (int, float)):
                temp_part = f"{temp:.1f}°C"
            else:
                temp_part = str(temp)
            return (
                f"Today's weather in {city}: {description}, {temp_part} {emoji} "
                f"{self.HASHTAG}"
            )

        if content_type == "recommendations" and recommendations:
            lines = recommendations.split("\n")
            first_rec = lines[1] if len(lines) > 1 else "Fun things to do!"
            return f"Exploring {city}? Try this: {first_rec} 🌟 {self.HASHTAG}"

        return f"Checking out {city} with Clima Mind! 🌍 {self.HASHTAG}"

    @staticmethod
    def _weather_emoji(main_cond: str) -> str:
        if main_cond == "clear":
            return "🌞"
        if main_cond in ("rain", "drizzle"):
            return "☔"
        if main_cond == "snow":
            return "❄️"
        return "☁️"
