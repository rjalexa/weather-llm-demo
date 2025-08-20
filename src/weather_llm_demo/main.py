from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from pathlib import Path
import os
from dotenv import load_dotenv
from .weather_agent import WeatherAgent
from .mcp_server import MCPWeatherServer
from .openrouter_client import OpenRouterClient
# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="Weather LLM Demo - Rome IROME8278")

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

# Italian system prompt
SYSTEM_PROMPT = """Sei un assistente meteorologico per Roma, Italia (Stazione IROME8278). 
Rispondi alla domanda nella stessa lingua in cui è stata posta e fai attenzione a personalizzare 
le raccomandazioni che generi in base alle condizioni meteo rilevate dall'agente. 
In particolare:
- Se la temperatura è superiore a 30 gradi ricorda che fa caldo e di vestirsi opportunamente e idratarsi bene
- Se fa meno di 16 gradi di coprirsi bene
- Se minaccia di piovere di munirsi di ombrello
- Fornisci sempre consigli pratici basati sulle condizioni attuali
- Usa emoji appropriate per rendere la risposta più amichevole"""


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
        weather_context = "\n\n[Dati meteo attuali da IROME8278]:\n"
        current = weather_data["result"]["current"]
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
    return {"status": "healthy", "service": "Weather LLM Demo", "station": "IROME8278"}


@app.get("/api/config")
async def get_config():
    """Get configuration information"""
    return {
        "llm_model": os.getenv("TOOL_CALLING_OPENROUTER_LLM_MODEL", "openai/gpt-3.5-turbo"),
        "station_id": os.getenv("STATION_ID", "IROME8278"),
        "location": os.getenv("LOCATION", "Rome, Italy")
    }


if __name__ == "__main__":
    import uvicorn

    print("🌤️  Starting Weather LLM Demo Server...")
    print("📍 Station: Rome IROME8278")
    print("🔗 Open http://localhost:8000 in your browser")
    uvicorn.run(app, host="0.0.0.0", port=8000)
