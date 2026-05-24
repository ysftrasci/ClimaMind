"""Application-wide configuration (secrets loaded from `.env`)."""

import os
from pathlib import Path

from dotenv import load_dotenv

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
load_dotenv(_PROJECT_ROOT / ".env")

# OpenWeatherMap
API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

# SMTP (e.g. Gmail)
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_SENDER_EMAIL = os.getenv("SMTP_SENDER_EMAIL", "")
SMTP_SENDER_PASSWORD = os.getenv("SMTP_SENDER_PASSWORD", "")

# Reminder scheduling day names (English display ↔ schedule library)
DAYS_OF_WEEK_EN = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]
DAYS_OF_WEEK_SCHEDULE = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]
DAY_MAP_EN_TO_SCHEDULE = dict(zip(DAYS_OF_WEEK_EN, DAYS_OF_WEEK_SCHEDULE))
