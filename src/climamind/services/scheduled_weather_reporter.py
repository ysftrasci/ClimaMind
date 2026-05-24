"""Scheduled email reports with current weather and advice."""

from climamind.infrastructure.api.openweather_client import OpenWeatherClient, WeatherError
from climamind.infrastructure.email.smtp_email_sender import EmailError, SmtpEmailSender
from climamind.services.weather_advisor import WeatherAdvisor


class ScheduledWeatherReporter:
    """
    Fetches weather, builds the reminder email body, and sends it.

    Mirrors ``send_scheduled_weather_report`` from maincode.py.
    """

    def __init__(
        self,
        weather_client: OpenWeatherClient | None = None,
        email_sender: SmtpEmailSender | None = None,
    ) -> None:
        self._weather_client = weather_client or OpenWeatherClient()
        self._email_sender = email_sender or SmtpEmailSender()

    def send_report(self, email: str, city: str) -> bool:
        """
        Send a weather reminder email for *city* to *email*.

        Returns:
            True if the email was sent, False if weather could not be fetched.
        """
        print(
            f"⏰ Running scheduled task: Fetching weather for {city} "
            f"for user {email}..."
        )
        try:
            weather = self._weather_client.fetch_current(city)
        except WeatherError:
            print(
                f"❌ Could not fetch weather for scheduled task: {city} "
                f"(User: {email})"
            )
            return False

        advice = WeatherAdvisor.get_advice(weather.main)
        sky_description = weather.description.capitalize()
        body = (
            f"Hello!\n\n"
            f"📍 Your daily weather report for {city}:\n"
            f"🌡️ Temperature: {weather.temp:.1f}°C\n"
            f"🌤️ Condition: {sky_description}\n\n"
            f"💡 {advice}\n\n"
            f"Best regards,\n"
            f"-- Clima Mind --"
        )
        subject = f"📅 Your {city} Weather Reminder"

        try:
            self._email_sender.send(email, subject, body)
            return True
        except EmailError as exc:
            print(
                f"❌ Could not send scheduled weather email to {email} "
                f"for {city}: {exc}"
            )
            return False
