"""Weather data transfer objects (OpenWeatherMap-shaped)."""

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass
class CurrentWeather:
    """Current conditions for a city."""

    temp: float
    description: str
    icon: str
    main: str
    lat: float | None = None
    lon: float | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "temp": self.temp,
            "description": self.description,
            "icon": self.icon,
            "main": self.main,
        }
        if self.lat is not None and self.lon is not None:
            result["lat"] = self.lat
            result["lon"] = self.lon
        return result

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "CurrentWeather":
        return cls(
            temp=float(data["temp"]),
            description=str(data["description"]),
            icon=str(data["icon"]),
            main=str(data["main"]),
            lat=data.get("lat"),
            lon=data.get("lon"),
        )


@dataclass
class DailyForecast:
    """One day in a multi-day forecast."""

    date: str
    temp: float
    description: str
    main: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "date": self.date,
            "temp": self.temp,
            "description": self.description,
            "main": self.main,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "DailyForecast":
        return cls(
            date=str(data["date"]),
            temp=float(data["temp"]),
            description=str(data["description"]),
            main=str(data["main"]),
        )
