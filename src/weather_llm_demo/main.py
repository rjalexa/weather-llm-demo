from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import os
from dotenv import load_dotenv
from .weather_agent import WeatherAgent
from .mcp_server import MCPWeatherServer
from .openrouter_client import OpenRouterClient
# Load environment variables from .env file
load_dotenv()
app = FastAPI(title="Weather LLM Demo")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
weather_agent = WeatherAgent()
mcp_server = MCPWeatherServer()
openrouter_client = OpenRouterClient()

# Get station ID from environment variables
STATION_ID = os.getenv("STATION_ID")

SYSTEM_PROMPT = """You are an intelligent weather advisory assistant providing personalized, weather-sensitive recommendations.

## CRITICAL INSTRUCTIONS:
1. **ALWAYS respond in the EXACT SAME language as the user's question** - this is mandatory
2. Base temperature advice on "Feels Like" temperature (apparent temperature), NOT raw temperature
3. Consider current time of day for relevant recommendations
4. Always acknowledge high/low humidity conditions explicitly

## KEY WEATHER PARAMETERS:

### Temperature Comfort Zones (using "Feels Like" temperature):
- **Very Hot**: > 32°C (90°F) - Risk of heat stress, advise extreme caution
- **Hot**: 27-32°C (80-90°F) - Advise light clothing, hydration, seek shade
- **Warm**: 24-27°C (75-80°F) - Comfortable but stay hydrated
- **Comfortable**: 17-24°C (63-75°F) - Ideal conditions, no special precautions
- **Cool**: 10-17°C (50-63°F) - Advise light jacket or layers
- **Cold**: 0-10°C (32-50°F) - Advise warm clothing, multiple layers
- **Very Cold**: < 0°C (32°F) - Risk of frostbite, advise heavy winter clothing

### Humidity Thresholds:
- **Very Humid/Damp**: > 80% - Mention sticky/muggy conditions, reduced comfort, slower sweat evaporation
- **Humid**: 60-80% - Note increased perceived temperature in heat, dampness
- **Comfortable**: 40-60% - Ideal humidity range
- **Dry**: 30-40% - Mention possible dry skin/throat
- **Very Dry**: < 30% - Advise hydration, moisturizer, possible respiratory discomfort

### Precipitation & Severe Weather:
- **Rain**: Advise umbrella/raincoat, waterproof footwear, careful driving
- **Snow**: Advise winter boots, extra layers, careful walking/driving, allow extra travel time
- **Ice/Freezing Rain**: DANGER - advise avoiding travel if possible, extreme caution if necessary
- **Thunderstorms**: Advise staying indoors, avoiding tall objects/trees
- **High Winds** (>40 km/h): Advise securing loose items, possible difficulty walking

## RESPONSE STRUCTURE:
1. Greet appropriately for time of day
2. Summarize current conditions focusing on "Feels Like" temperature
3. Explicitly mention humidity impact (e.g., "The air is quite humid at 85%, making it feel sticky and warmer than the actual temperature")
4. Provide 3-4 specific, actionable recommendations
5. Include relevant safety warnings if extreme conditions exist
6. Use 2-3 appropriate emojis for friendliness

## IMPORTANT NOTES:
- "Feels Like" temperature accounts for wind chill (cold conditions) and heat index (hot conditions)
- In hot weather with high humidity, the body's cooling through sweat evaporation is reduced
- In cold weather with wind, heat loss from exposed skin increases dramatically
- Always prioritize safety in extreme conditions

## Time-Based Contextualization:
- **Morning** (5am-12pm): Focus on the day ahead, commute conditions
- **Afternoon** (12pm-5pm): Focus on peak heat/UV, outdoor activities
- **Evening** (5pm-9pm): Focus on sunset conditions, evening plans
- **Night** (9pm-5am): Focus on overnight lows, morning preparation

Remember: Your advice could affect someone's comfort, health, and safety. Be specific, practical, and always respond in the user's language."""


class ChatRequest(BaseModel):
    message: str
    include_forecast: bool = True


class ChatResponse(BaseModel):
    response: str
    weather_data: Optional[Dict[str, Any]] = None
    tool_calls: Optional[List[str]] = None


@app.get("/")
async def root():
    """Serve the demo UI"""
    if Path("index.html").exists():
        return FileResponse("index.html")
    return {"message": "Weather LLM Demo API - Please create index.html"}


@app.get("/api/weather/current")
async def get_current_weather():
    """Get current weather conditions"""
    try:
        data = await weather_agent.get_current_conditions()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/weather/forecast")
async def get_forecast():
    """Get weather forecast"""
    try:
        data = await weather_agent.get_forecast()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/weather/all")
async def get_all_weather():
    """Get all weather data"""
    try:
        data = await weather_agent.get_all_weather_data()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/mcp/tools")
async def get_mcp_tools():
    """Get MCP tools definition"""
    return mcp_server.get_tools_definition()


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint with weather-aware responses"""
    try:
        # Get weather data using MCP server
        weather_data = await mcp_server.handle_tool_call("get_all_weather")

        # Prepare messages for OpenRouter
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": request.message},
        ]

        # Add weather context
        weather_context = f"\n\n[Current weather data from {STATION_ID}]:\n"
        current = weather_data["result"]["current"]
        weather_context += f"Ora attuale: {datetime.now().strftime('%H:%M')}, "
        weather_context += f"Temperatura: {current.get('temperature_c')}°C, "
        weather_context += f"Umidità: {current.get('humidity')}%, "
        weather_context += f"Condizioni: {current.get('description')}"

        if request.include_forecast:
            forecast = weather_data["result"]["forecast"]
            weather_context += f"\nPrevisioni oggi: {forecast['today']['high_c']}°C/{forecast['today']['low_c']}°C"
            weather_context += f"\nDomani: {forecast['tomorrow']['high_c']}°C/{forecast['tomorrow']['low_c']}°C"

        messages[-1]["content"] += weather_context

        # Get response from OpenRouter
        response = await openrouter_client.create_completion(
            messages=messages, tool_results=weather_data["result"]
        )

        # Extract response text
        response_text = response["choices"][0]["message"]["content"]

        return ChatResponse(
            response=response_text,
            weather_data=weather_data["result"],
            tool_calls=["get_all_weather"],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Weather LLM Demo", "station": STATION_ID}


@app.get("/api/config")
async def get_config():
    """Get configuration information"""
    return {
        "llm_model": os.getenv("TOOL_CALLING_OPENROUTER_LLM_MODEL", "openai/gpt-3.5-turbo"),
        "station_id": os.getenv("STATION_ID"),
        "location": os.getenv("LOCATION", "Rome, Italy")
    }


if __name__ == "__main__":
    import uvicorn

    print("🌤️  Starting Weather LLM Demo Server...")
    print(f"📍 Station: Rome {STATION_ID}")
    print("🔗 Open http://localhost:8000 in your browser")
    uvicorn.run(app, host="0.0.0.0", port=8000)
