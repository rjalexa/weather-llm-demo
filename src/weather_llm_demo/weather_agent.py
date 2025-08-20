import httpx
import json
from bs4 import BeautifulSoup
from typing import Dict, Any
from datetime import datetime


class WeatherAgent:
    """Weather agent that scrapes Weather Underground data"""

    def __init__(self):
        self.station_url = "https://www.wunderground.com/dashboard/pws/IROME8278"
        self.forecast_url = "https://www.wunderground.com/weather/it/rome/IROME8278"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    async def get_current_conditions(self) -> Dict[str, Any]:
        """Fetch and parse current weather conditions from Weather Underground"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.station_url, headers=self.headers)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")
            script = soup.find("script", {"id": "app-root-state"})
            if not script:
                raise ValueError("Could not find app-root-state script tag")
            
            script_content = script.get_text()
            if not script_content:
                raise ValueError("Script tag is empty")

            data = json.loads(script_content)
            
            latest_obs = None
            for key in data:
                if isinstance(data[key], dict) and "b" in data[key] and isinstance(data[key]["b"], dict) and "observations" in data[key]["b"]:
                    if data[key]["b"]["observations"]:
                        latest_obs = data[key]["b"]["observations"][-1]
                        break
            
            if not latest_obs:
                raise ValueError("Could not find observations data in JSON")

            imperial = latest_obs.get("imperial", {})
            
            def f_to_c(f):
                return round((f - 32) * 5 / 9, 1) if f is not None else None

            conditions = {
                "temperature_c": f_to_c(imperial.get("tempAvg")),
                "humidity": latest_obs.get("humidityAvg"),
                "wind_kmh": imperial.get("windspeedAvg"),
                "pressure_mb": imperial.get("pressureMax"),
                "feels_like_c": f_to_c(imperial.get("heatindexAvg")),
                "uv_index": latest_obs.get("uvHigh"),
                "description": "Scraped from Weather Underground JSON",
                "timestamp": datetime.now().isoformat(),
                "station": "IROME8278",
            }
            
            if conditions["wind_kmh"] is not None:
                conditions["wind_kmh"] = round(conditions["wind_kmh"] * 1.60934, 1)
            if conditions["pressure_mb"] is not None:
                conditions["pressure_mb"] = round(conditions["pressure_mb"] * 33.8639, 1)

            return conditions

        except Exception as e:
            return {
                "error": str(e),
                "note": "Using fallback demo data due to scraping error",
                "temperature_c": 24.5,
                "humidity": 65,
                "wind_kmh": 12.0,
                "description": "Partly Cloudy (fallback)",
                "pressure_mb": 1015,
                "feels_like_c": 25.0,
                "uv_index": 4,
                "timestamp": datetime.now().isoformat(),
                "station": "IROME8278",
            }

    async def get_forecast(self) -> Dict[str, Any]:
        """Fetch and parse weather forecast from Weather Underground"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.forecast_url, headers=self.headers)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")
            script = soup.find("script", {"id": "app-root-state"})
            if not script:
                raise ValueError("Could not find app-root-state script tag")

            script_content = script.get_text()
            if not script_content:
                raise ValueError("Script tag is empty")

            data = json.loads(script_content)

            forecast_data = None
            for key in data:
                if isinstance(data[key], dict) and "b" in data[key] and isinstance(data[key]["b"], dict) and "daypart" in data[key]["b"]:
                    forecast_data = data[key]["b"]
                    break
            
            if not forecast_data:
                raise ValueError("Could not find forecast data in JSON")

            def f_to_c(f):
                return round((f - 32) * 5 / 9, 1) if f is not None else None

            today_forecast = {
                "high_c": f_to_c(forecast_data["calendarDayTemperatureMax"][0]),
                "low_c": f_to_c(forecast_data["calendarDayTemperatureMin"][0]),
                "conditions": forecast_data["narrative"][0],
                "precipitation_chance": forecast_data["daypart"][0]["precipChance"][1],
                "wind_kmh": round(forecast_data["daypart"][0].get("windSpeed", [])[1] * 1.60934, 1),
            }
            
            tomorrow_forecast = {
                "high_c": f_to_c(forecast_data["calendarDayTemperatureMax"][1]),
                "low_c": f_to_c(forecast_data["calendarDayTemperatureMin"][1]),
                "conditions": forecast_data["narrative"][1],
                "precipitation_chance": forecast_data["daypart"][0]["precipChance"][2],
                "wind_kmh": round(forecast_data["daypart"][0].get("windSpeed", [])[2] * 1.60934, 1),
            }

            return {
                "today": today_forecast,
                "tomorrow": tomorrow_forecast,
                "extended": []
            }

        except Exception as e:
            return {
                "error": str(e),
                "note": "Using fallback demo data due to scraping error",
                "today": {"high_c": 28, "low_c": 18, "conditions": "Partly Cloudy (fallback)"},
                "tomorrow": {"high_c": 30, "low_c": 19, "conditions": "Sunny (fallback)"},
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
