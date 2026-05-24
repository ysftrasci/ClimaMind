"""Weather advice and recommendation text generation (no API or UI)."""

from climamind.domain.models.weather import CurrentWeather, DailyForecast


class WeatherAdvisor:
    """Builds user-facing advice strings from weather domain models."""

    ADVICE_MAP: dict[str, str] = {
        "rain": "Don't forget your umbrella!",
        "drizzle": "Don't forget your umbrella!",
        "snow": "Dress warmly, it's snowy!",
        "clear": "Enjoy the clear skies!",
        "clouds": "It looks cloudy today.",
        "mist": "Be careful, it's foggy/misty!",
        "fog": "Be careful, it's foggy/misty!",
    }

    @classmethod
    def get_advice(cls, main_condition: str) -> str:
        """Short tip for email/search/reminder bodies (unified advice_map)."""
        main = main_condition.lower()
        if main in cls.ADVICE_MAP:
            return cls.ADVICE_MAP[main]
        if main in ("mist", "fog"):
            return "Be careful, it's foggy/misty!"
        return "Have a great day!"

    @classmethod
    def format_weekly_forecast(
        cls, city: str, forecast: list[DailyForecast]
    ) -> str | None:
        """Format a multi-day forecast as plain text (mirrors process_weekly_forecast)."""
        if not forecast:
            return None
        result = f"{city} Expected Weather Situation:\n"
        for day in forecast:
            result += f"{day.date}: {day.description}, {day.temp:.1f}°C\n"
        return result

    @classmethod
    def format_dangerous_conditions(
        cls, city: str, weather: CurrentWeather
    ) -> str:
        """Safety summary for current conditions (mirrors process_dangerous_conditions)."""
        temp = weather.temp
        main_cond = weather.main.lower()

        warnings: list[str] = []
        if main_cond in ("rain", "drizzle"):
            warnings.append(
                "Rain is expected today. Don't forget your umbrella! ☔"
            )
        if main_cond == "snow":
            warnings.append("Snow is expected today. Dress warmly! ❄️")
        if main_cond == "thunderstorm":
            warnings.append(
                "A storm is expected today. Stay safe indoors! ⚡️"
            )
        if temp > 35:
            warnings.append(
                f"Extreme heat today at {temp:.1f}°C. "
                "Stay hydrated and keep cool! 🔥"
            )

        if warnings:
            return f"Dangerous conditions in {city}:\n" + "\n".join(warnings)
        return (
            f"No dangerous conditions in {city} today. "
            f"Weather is {weather.description}, {temp:.1f}°C."
        )

    @classmethod
    def format_activity_recommendations(
        cls, city: str, weather: CurrentWeather
    ) -> str:
        """Activity and warning lists (mirrors process_activity_recommendations)."""
        temp = weather.temp
        main_cond = weather.main.lower()
        description = weather.description.lower()

        recommendations: list[str] = []
        warnings: list[str] = []

        if temp < 0:
            temp_category = "very cold"
            recommendations.extend(
                [
                    "Enjoy a hot soup or herbal tea at home. 🍵",
                    "Curl up with a blanket and watch a favorite movie. 🎬",
                    "Do light exercise at an indoor gym. 🏋️",
                    "Discover a new book at the library. 📚",
                ]
            )
            warnings.extend(
                [
                    "Wear a heavy coat, scarf, and gloves if going outside! 🧣",
                    "Watch out for icy surfaces, they can be slippery. ❄️",
                    "Use moisturizer to protect your skin. 🧴",
                ]
            )
        elif 0 <= temp <= 10:
            temp_category = "cold"
            recommendations.extend(
                [
                    "Grab a hot coffee at a cozy café. ☕",
                    "Spend time at a museum or art gallery. 🖼️",
                    "Have fun with a puzzle or board game at home. 🎲",
                    "Go for a brisk walk in the park, but dress warmly. 🌳",
                ]
            )
            warnings.extend(
                [
                    "Avoid staying outside too long to prevent catching a cold. 🥶",
                    "Don't forget to take vitamin C to stay healthy. 🍊",
                ]
            )
        elif 10 < temp <= 20:
            temp_category = "mild"
            recommendations.extend(
                [
                    "Take a walk or bike ride in the park. 🚴",
                    "Organize a picnic with friends. 🧺",
                    "Go photography in the open air. 📸",
                    "Read a book or meditate in the garden. 🧘",
                    "Visit a local market for fresh produce. 🛍️",
                ]
            )
            warnings.extend(
                [
                    "Bring a light jacket, it might get chilly in the evening. 🧥",
                    "Watch out for pollen if you have allergies. 🌾",
                ]
            )
        elif 20 < temp <= 30:
            temp_category = "warm"
            recommendations.extend(
                [
                    "Head to the beach or pool to cool off. 🏊",
                    "Enjoy an ice cream while strolling by the seaside. 🍦",
                    "Watch a movie at an outdoor cinema. 🎥",
                    "Take a bike tour around the city. 🚲",
                    "Host a barbecue party. 🍔",
                ]
            )
            warnings.extend(
                [
                    "Don't forget to apply sunscreen! ☀️",
                    "Drink plenty of water to stay hydrated. 🥤",
                    "Avoid direct sun during midday hours. 🕶️",
                ]
            )
        else:
            temp_category = "very hot"
            recommendations.extend(
                [
                    "Explore an air-conditioned shopping mall. 🏬",
                    "Sip cold drinks at a café. 🧃",
                    "Take a refreshing shower and relax at home. 🚿",
                    "Go for a short walk in the cooler evening. 🌅",
                    "Tour a museum for a cool cultural experience. 🏛️",
                ]
            )
            warnings.extend(
                [
                    "Stay in the shade to avoid heatstroke! 🌴",
                    "Wear light, loose-fitting clothing. 👕",
                    "Drink lots of water to prevent dehydration. 💧",
                ]
            )

        if main_cond == "clear" or (main_cond == "clouds" and "few" in description):
            recommendations.extend(
                [
                    "Enjoy the sunshine with a picnic! 🌞",
                    "Go hiking and enjoy the scenic views. 🏞️",
                    "Fly a kite, it's perfect weather for it. 🪁",
                ]
            )
            warnings.append("Wear sunglasses to protect your eyes. 🕶️")
        elif main_cond in ("rain", "drizzle"):
            recommendations.extend(
                [
                    "Watch the rain from a café while sipping coffee. ☔",
                    "Have fun at an indoor arcade. 🎮",
                    "Learn to cook at home, try new recipes. 🍳",
                    "Catch a new movie at the cinema. 🎞️",
                ]
            )
            warnings.extend(
                [
                    "Don't forget your umbrella or raincoat! ☂️",
                    "Be careful on wet surfaces to avoid slipping.",
                ]
            )
        elif main_cond == "snow":
            recommendations.extend(
                [
                    "Build a snowman or have a snowball fight! ❄️",
                    "Sip hot chocolate while watching the snow. ☕",
                    "Try ice skating at an indoor rink. ⛸️",
                ]
            )
            warnings.extend(
                [
                    "Wear warm, waterproof clothing. 🧤",
                    "Watch out for snow piles and icy roads. 🚶",
                ]
            )
        elif main_cond == "thunderstorm":
            recommendations.extend(
                [
                    "Stay in and binge-watch a series. 📺",
                    "Play board games with family. 🎲",
                    "Take an online course to learn something new. 💻",
                ]
            )
            warnings.extend(
                [
                    "Avoid going outside during the storm, stay safe! ⚡️",
                    "Unplug electronics to protect them from lightning.",
                ]
            )
        elif main_cond in ("mist", "fog"):
            recommendations.extend(
                [
                    "Cozy up with a good book in the fog. 📖",
                    "Practice yoga at an indoor studio. 🧘",
                    "Host a movie marathon with friends. 🍿",
                ]
            )
            warnings.extend(
                [
                    "Visibility is low, drive slowly if necessary. 🌫️",
                    "Wear reflective clothing to stay visible.",
                ]
            )
        elif main_cond == "clouds":
            recommendations.extend(
                [
                    "Play a match at an indoor sports facility. ⚽",
                    "Get creative with painting or crafts at home. 🎨",
                    "Visit an art exhibition for inspiration. 🖌️",
                ]
            )
            warnings.append("Weather might change, keep a jacket handy. 🧥")
        else:
            recommendations.extend(
                [
                    "Spend time indoors at a café or museum. ☕",
                    "Try a new hobby like knitting at home. 🧶",
                    "Host a game night with friends. 🎲",
                ]
            )
            warnings.append(
                "Air quality might be poor, consider wearing a mask. 😷"
            )

        result = (
            f"Recommendations for {city} ({temp_category}, "
            f"{description.capitalize()}):\n"
        )
        result += "\n📌 Recommendations:\n" + "\n".join(recommendations[:5])
        result += "\n\n⚠️ Warnings:\n" + "\n".join(warnings[:3])
        return result
