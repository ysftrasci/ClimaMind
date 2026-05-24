"""Joyuci assistant: query handling, chat history, response text."""

from dataclasses import dataclass, field

from climamind.domain.models.chat import ChatEntry
from climamind.domain.models.user import User
from climamind.domain.models.weather import CurrentWeather, DailyForecast
from climamind.infrastructure.api.openweather_client import OpenWeatherClient, WeatherError
from climamind.infrastructure.persistence.user_repository import UserRepository
from climamind.services.exceptions import EmptyQueryError
from climamind.services.query_parser import QueryParser
from climamind.services.weather_advisor import WeatherAdvisor

CHAT_HISTORY_LIMIT = 10


@dataclass
class JoyuciResponse:
    """Result returned to the Joyuci UI layer."""

    query: str
    response_text: str
    success: bool
    feature: str | None = None
    city: str | None = None
    weekly_forecast: list[DailyForecast] = field(default_factory=list)
    current_weather: CurrentWeather | None = None
    recommendations_text: str | None = None


class JoyuciService:
    """
    Processes Joyuci chat queries and manages per-user history.

    Weather fetching uses ``OpenWeatherClient``; text uses ``WeatherAdvisor``.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        query_parser: QueryParser | None = None,
        weather_client: OpenWeatherClient | None = None,
    ) -> None:
        self._user_repository = user_repository
        self._parser = query_parser or QueryParser()
        self._weather_client = weather_client or OpenWeatherClient()
        self._advisor = WeatherAdvisor()

    def get_chat_history(self, email: str) -> list[ChatEntry]:
        users = self._user_repository.load_all()
        user = users.get(email.strip().lower())
        if not user:
            return []
        return list(user.chat_history)

    def format_chat_history_text(self, history: list[ChatEntry]) -> str:
        """Plain text for the chat history Text widget."""
        lines: list[str] = []
        for entry in history:
            lines.append(f"You: {entry.query}\nJoyuci: {entry.response}\n")
        return "\n".join(lines)

    def clear_chat_history(self, email: str) -> None:
        users = self._user_repository.load_all()
        email = email.strip().lower()
        if email in users:
            users[email].chat_history = []
            self._user_repository.save_all(users)

    def process_query(
        self, email: str, query: str, username: str
    ) -> JoyuciResponse:
        """
        Parse *query*, fetch weather if needed, persist chat entry.

        Mirrors ``submit_joyuci_query`` logic from maincode.py.
        """
        query = query.strip()
        if not query:
            raise EmptyQueryError("Please type something for me to work with!")

        parsed = self._parser.parse(query)
        if not parsed.is_valid:
            error_message = (
                f"Oops, {username}! I didn't catch that. Try something like "
                f"'Weather in İstanbul' or 'What to do in İzmir'!"
            )
            self._append_chat_entry(email, query, error_message)
            return JoyuciResponse(
                query=query,
                response_text=error_message,
                success=False,
                feature=parsed.feature,
                city=parsed.city,
            )

        feature = parsed.feature
        city = parsed.city
        assert feature and city

        result: str | None = None
        weekly_forecast: list[DailyForecast] = []
        recommendations_text: str | None = None
        current_weather: CurrentWeather | None = None

        try:
            if feature == QueryParser.FEATURE_WEEKLY:
                weekly_forecast = self._weather_client.fetch_weekly_forecast(city)
                raw = self._advisor.format_weekly_forecast(city, weekly_forecast)
                if raw:
                    result = (
                        f"Hey {username}, here's the 5-day forecast for {city}:\n"
                        f"{raw}"
                    )
            elif feature == QueryParser.FEATURE_DANGEROUS:
                current_weather = self._weather_client.fetch_current(city)
                raw = self._advisor.format_dangerous_conditions(
                    city, current_weather
                )
                result = (
                    f"Alright {username}, here's the safety check for {city}:\n"
                    f"{raw}\nStay safe out there!"
                )
            elif feature == QueryParser.FEATURE_ACTIVITY:
                current_weather = self._weather_client.fetch_current(city)
                raw = self._advisor.format_activity_recommendations(
                    city, current_weather
                )
                result = (
                    f"Hi {username}! Looking for fun in {city}? "
                    f"Here's what I suggest:\n{raw}"
                )
                recommendations_text = raw
        except WeatherError:
            result = None

        if result:
            if current_weather is None:
                try:
                    current_weather = self._weather_client.fetch_current(city)
                except WeatherError:
                    current_weather = None

            self._append_chat_entry(email, query, result)
            return JoyuciResponse(
                query=query,
                response_text=result,
                success=True,
                feature=feature,
                city=city,
                weekly_forecast=weekly_forecast,
                current_weather=current_weather,
                recommendations_text=recommendations_text,
            )

        error_message = f"Sorry {username}, I couldn't find any info for {city}."
        self._append_chat_entry(email, query, error_message)
        return JoyuciResponse(
            query=query,
            response_text=error_message,
            success=False,
            feature=feature,
            city=city,
        )

    def resolve_username(self, email: str) -> str:
        """Display name from account profile or email local-part."""
        users = self._user_repository.load_all()
        user = users.get(email.strip().lower())
        if not user:
            return email.split("@")[0]
        name = user.account.username.strip()
        return name if name else email.split("@")[0]

    def _append_chat_entry(self, email: str, query: str, response: str) -> list[ChatEntry]:
        users = self._user_repository.load_all()
        email = email.strip().lower()
        user = users.setdefault(email, User())
        history = user.chat_history
        history.append(ChatEntry(query=query, response=response))
        if len(history) > CHAT_HISTORY_LIMIT:
            history.pop(0)
        self._user_repository.save_all(users)
        return list(history)
