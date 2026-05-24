"""Favorite cities persistence and validation."""

from climamind.domain.models.user import User
from climamind.infrastructure.api.openweather_client import OpenWeatherClient, WeatherError
from climamind.infrastructure.persistence.user_repository import UserRepository


class FavoritesError(Exception):
    """Base class for favorites operations."""


class NotAuthenticatedError(FavoritesError):
    """User must be logged in."""


class CityAlreadyFavoriteError(FavoritesError):
    """City is already in favorites."""


class CityNotInFavoritesError(FavoritesError):
    """City is not in the user's favorites."""


class InvalidCityError(FavoritesError):
    """City could not be validated via weather API."""


class FavoritesService:
    def __init__(
        self,
        user_repository: UserRepository,
        weather_client: OpenWeatherClient | None = None,
    ) -> None:
        self._user_repository = user_repository
        self._weather_client = weather_client or OpenWeatherClient()

    def list_favorites(self, email: str) -> list[str]:
        user = self._get_user(email)
        return list(user.favorites)

    def add_favorite(self, email: str, city: str) -> list[str]:
        city = city.strip().title()
        if not city:
            raise FavoritesError("Please enter a city name!")
        user = self._get_user(email)
        if city in user.favorites:
            raise CityAlreadyFavoriteError(f"'{city}' is already in your favorites!")
        try:
            self._weather_client.fetch_current(city)
        except WeatherError as exc:
            raise InvalidCityError(f"Could not find weather data for '{city}'.") from exc
        user.favorites.append(city)
        self._save(user, email)
        return list(user.favorites)

    def remove_favorite(self, email: str, city: str) -> list[str]:
        user = self._get_user(email)
        if city not in user.favorites:
            raise CityNotInFavoritesError("City not in favorites.")
        user.favorites.remove(city)
        self._save(user, email)
        return list(user.favorites)

    def _get_user(self, email: str) -> User:
        if not email:
            raise NotAuthenticatedError("You must be logged in.")
        email = email.strip().lower()
        users = self._user_repository.load_all()
        if email not in users:
            raise NotAuthenticatedError("User not found.")
        return users[email]

    def _save(self, user: User, email: str) -> None:
        users = self._user_repository.load_all()
        users[email] = user
        if not self._user_repository.save_all(users):
            raise FavoritesError("Could not save favorites.")
