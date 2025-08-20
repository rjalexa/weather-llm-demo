from typing import Dict, Any
from datetime import datetime


class WeatherAgent:
    """Weather agent that scrapes Weather Underground data"""

    def __init__(self):
        self.station_url = "https://www.wunderground.com/dashboard/pws/IROME8278"
        self.forecast_url = "https://www.wunderground.com/weather/it/rome/IROME8278"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    async def get_current_conditions(self) -> Dict[str, Any]:
        """Fetch current weather conditions"""
        try:
            # For demo purposes, returning simulated data
            # Real implementation would scrape the actual website
            return {
                "temperature_c": 24.5,
                "humidity": 65,
                "wind_kmh": 12.0,
                "description": "Partly Cloudy",
                "pressure_mb": 1015,
                "feels_like_c": 25.0,
                "uv_index": 4,
                "visibility_km": 10,
                "timestamp": datetime.now().isoformat(),
                "station": "IROME8278",
            }
        except Exception as e:
            return {"error": str(e), "note": "Using demo data"}

    async def get_forecast(self) -> Dict[str, Any]:
        """Fetch weather forecast"""
        return {
            "today": {
                "high_c": 28,
                "low_c": 18,
                "conditions": "Partly Cloudy",
                "precipitation_chance": 20,
                "wind_kmh": 15,
            },
            "tomorrow": {
                "high_c": 30,
                "low_c": 19,
                "conditions": "Sunny",
                "precipitation_chance": 10,
                "wind_kmh": 12,
            },
            "extended": [
                {
                    "day": "Day 3",
                    "high_c": 29,
                    "low_c": 20,
                    "conditions": "Mostly Sunny",
                },
                {"day": "Day 4", "high_c": 27, "low_c": 18, "conditions": "Cloudy"},
                {
                    "day": "Day 5",
                    "high_c": 25,
                    "low_c": 17,
                    "conditions": "Rainy",
                    "precipitation_chance": 70,
                },
            ],
        }

    async def get_all_weather_data(self) -> Dict[str, Any]:
        """Get both current conditions and forecast"""
        current = await self.get_current_conditions()
        forecast = await self.get_forecast()

        return {
            "current": current,
            "forecast": forecast,
            "location": "Rome, Italy",
            "station_id": "IROME8278",
        }
