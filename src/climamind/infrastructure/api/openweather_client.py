"""OpenWeatherMap HTTP client (no UI dependencies)."""

from urllib.parse import quote

import requests

from climamind.config.settings import API_KEY
from climamind.domain.models.weather import CurrentWeather, DailyForecast


class WeatherError(Exception):
    """Base class for weather API failures."""

    def __init__(self, message: str, city: str | None = None) -> None:
        self.city = city
        super().__init__(message)


class EmptyCityError(WeatherError):
    """Raised when the city name is missing."""


class ApiKeyNotConfiguredError(WeatherError):
    """Raised when the OpenWeatherMap API key is not set."""


class CityNotFoundError(WeatherError):
    """Raised when the API returns 404 for a city."""


class InvalidApiKeyError(WeatherError):
    """Raised when the API returns 401 (invalid API key)."""


class WeatherTimeoutError(WeatherError):
    """Raised when the HTTP request times out."""


class WeatherConnectionError(WeatherError):
    """Raised when the request cannot reach the weather server."""


class WeatherHttpError(WeatherError):
    """Raised for other HTTP error responses."""

    def __init__(self, message: str, city: str | None = None, status_code: int | None = None) -> None:
        self.status_code = status_code
        super().__init__(message, city)


class WeatherDataError(WeatherError):
    """Raised when the response body is missing expected fields."""


class OpenWeatherClient:
    """Fetches current weather and multi-day forecasts from OpenWeatherMap."""

    _CURRENT_URL = "http://api.openweathermap.org/data/2.5/weather"
    _FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast"

    def __init__(self, api_key: str | None = None, timeout: int = 10) -> None:
        self._api_key = api_key if api_key is not None else API_KEY
        self._timeout = timeout

    def fetch_current(self, city: str) -> CurrentWeather:
        """Return current weather for *city*."""
        city = self._validate_city(city)
        self._validate_api_key()
        url = self._current_url(city)
        print(f"DEBUG: API URL: {url}")
        data = self._get_json(url, city)
        return self._parse_current(data, city)

    def fetch_weekly_forecast(self, city: str) -> list[DailyForecast]:
        """Return up to five daily forecast entries (noon snapshots)."""
        city = self._validate_city(city)
        self._validate_api_key()
        url = self._forecast_url(city)
        print(f"DEBUG: API URL: {url}")
        data = self._get_json(url, city)
        return self._parse_weekly_forecast(data, city)

    def _validate_city(self, city: str) -> str:
        if not city or not str(city).strip():
            print("❌ City name is empty.")
            raise EmptyCityError("City name is empty.")
        return str(city).strip()

    def _validate_api_key(self) -> None:
        if not self._api_key or self._api_key == "YOUR_API_KEY":
            print("❌ OpenWeatherMap API key is not set.")
            raise ApiKeyNotConfiguredError("OpenWeatherMap API key is not set.")

    def _current_url(self, city: str) -> str:
        return (
            f"{self._CURRENT_URL}?q={quote(city)}"
            f"&appid={self._api_key}&units=metric&lang=en"
        )

    def _forecast_url(self, city: str) -> str:
        return (
            f"{self._FORECAST_URL}?q={quote(city)}"
            f"&appid={self._api_key}&units=metric&lang=en"
        )

    def _get_json(self, url: str, city: str) -> dict:
        try:
            response = requests.get(url, timeout=self._timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout as exc:
            print(f"❌ Weather request timed out ({city}).")
            raise WeatherTimeoutError(
                f"Connection timed out while fetching weather for {city}.",
                city=city,
            ) from exc
        except requests.exceptions.HTTPError as exc:
            self._raise_for_http(exc, city)
            raise  # unreachable; _raise_for_http always raises
        except requests.exceptions.RequestException as exc:
            print(f"❌ Weather request error ({city}): {exc}")
            raise WeatherConnectionError(
                f"Could not connect to weather server for {city}. "
                "Check your internet connection.",
                city=city,
            ) from exc
        except Exception as exc:
            print(f"❌ Unexpected weather error ({city}): {exc}")
            raise WeatherError(
                f"An unknown error occurred while fetching weather for {city}: {exc}",
                city=city,
            ) from exc

    def _raise_for_http(self, exc: requests.exceptions.HTTPError, city: str) -> None:
        response = exc.response
        status = response.status_code if response is not None else None
        if status == 404:
            print(f"❌ City not found: {city}")
            raise CityNotFoundError(f"City not found: {city}", city=city) from exc
        if status == 401:
            print("❌ Invalid API key.")
            raise InvalidApiKeyError(
                "Invalid API key. Please check the program settings.",
            ) from exc
        print(f"❌ HTTP error ({city}): {exc}")
        raise WeatherHttpError(
            f"HTTP error fetching weather for {city}: {exc}",
            city=city,
            status_code=status,
        ) from exc

    def _parse_current(self, data: dict, city: str) -> CurrentWeather:
        try:
            if (
                "main" in data
                and "temp" in data["main"]
                and "weather" in data
                and data["weather"]
                and "description" in data["weather"][0]
                and "icon" in data["weather"][0]
            ):
                temp = data["main"]["temp"]
                sky_description = data["weather"][0]["description"].capitalize()
                icon_code = data["weather"][0]["icon"]
                main_condition = data["weather"][0]["main"].lower()
                lat = data.get("coord", {}).get("lat")
                lon = data.get("coord", {}).get("lon")

                if lat is None or lon is None:
                    print(f"⚠️ Coordinates not found for {city}")
                    return CurrentWeather(
                        temp=temp,
                        description=sky_description,
                        icon=icon_code,
                        main=main_condition,
                    )

                return CurrentWeather(
                    temp=temp,
                    description=sky_description,
                    icon=icon_code,
                    main=main_condition,
                    lat=lat,
                    lon=lon,
                )

            print(f"⚠️ Weather data incomplete or malformed ({city}): {data}")
            raise WeatherDataError(
                f"Could not process weather data for {city}.",
                city=city,
            )
        except (KeyError, IndexError, TypeError) as exc:
            print(f"❌ Error processing weather data ({city}): {exc}")
            raise WeatherDataError(
                f"Could not process weather data for {city}.",
                city=city,
            ) from exc

    def _parse_weekly_forecast(self, data: dict, city: str) -> list[DailyForecast]:
        try:
            if "list" not in data:
                print(f"❌ Weekly forecast data missing ({city}): {data}")
                raise WeatherDataError(
                    f"Weekly forecast data missing for {city}.",
                    city=city,
                )

            weekly_forecast: list[DailyForecast] = []
            seen_dates: set[str] = set()
            for entry in data["list"]:
                date_time = entry["dt_txt"]
                date = date_time.split(" ")[0]
                if "12:00:00" in date_time and date not in seen_dates:
                    seen_dates.add(date)
                    weekly_forecast.append(
                        DailyForecast(
                            date=date,
                            temp=entry["main"]["temp"],
                            description=entry["weather"][0]["description"].capitalize(),
                            main=entry["weather"][0]["main"].lower(),
                        )
                    )
                if len(weekly_forecast) >= 5:
                    break

            if not weekly_forecast:
                print(f"❌ No suitable forecast data found for {city}.")
                raise WeatherDataError(
                    f"No suitable forecast data found for {city}.",
                    city=city,
                )

            return weekly_forecast
        except WeatherDataError:
            raise
        except (KeyError, IndexError, TypeError) as exc:
            print(f"❌ Error processing weekly forecast data ({city}): {exc}")
            raise WeatherDataError(
                f"Could not process weekly forecast data for {city}.",
                city=city,
            ) from exc
