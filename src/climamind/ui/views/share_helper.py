"""Execute social share actions in the UI layer."""

from __future__ import annotations

import webbrowser

import pyperclip
from tkinter import messagebox

from climamind.context import AppContext
from climamind.domain.models.weather import CurrentWeather
from climamind.services.social_share_service import ShareAction, UnsupportedPlatformError


def execute_share(
    ctx: AppContext,
    city: str,
    platform: str,
    *,
    content_type: str = "weather",
    weather: CurrentWeather | None = None,
    recommendations: str | None = None,
) -> None:
    try:
        action: ShareAction = ctx.social_share_service.build_share(
            city,
            platform,
            content_type=content_type,
            weather_data=weather,
            recommendations=recommendations,
        )
        if action.clipboard_text:
            pyperclip.copy(action.clipboard_text)
        if action.user_notice:
            messagebox.showinfo(
                f"{platform.capitalize()} Share",
                action.user_notice,
            )
        if action.browser_url:
            webbrowser.open(action.browser_url)
        print(f"✅ Shared on {platform} for {city}: {action.message}")
    except UnsupportedPlatformError as exc:
        messagebox.showerror("Share Error", str(exc))
    except Exception as exc:
        print(f"❌ Error generating {platform} share link: {exc}")
        messagebox.showerror("Share Error", f"Could not prepare share link for {platform}: {exc}")
