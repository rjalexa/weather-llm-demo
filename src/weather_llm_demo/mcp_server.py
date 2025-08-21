"""MCP (Model Context Protocol) Server for Weather Agent"""

from typing import Dict, Any, List, Optional
from .weather_agent import WeatherAgent


class MCPWeatherServer:
    """MCP-compliant weather tool server"""

    def __init__(self):
        self.weather_agent = WeatherAgent()
        self.tools = self._define_tools()

    def _define_tools(self) -> List[Dict[str, Any]]:
        """Define available tools in MCP format"""
        # Define tools in OpenRouter format
        self.openrouter_tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_current_weather",
                    "description": "Get current weather conditions from Rome station IROME8278",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                }
            },
            {
                "type": "function",
                "function": {
                "name": "get_weather_forecast",
                "description": "Get weather forecast for Rome",
                "parameters": {"type": "object", "properties": {}, "required": []},
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_all_weather",
                    "description": "Get both current conditions and forecast",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                }
            },
        ]
        
        # Preserve existing MCP format for backward compatibility
        self.mcp_tools = [
            {
                "name": "get_current_weather",
                "description": "Get current weather conditions from Rome station IROME8278",
                "input_schema": {"type": "object", "properties": {}, "required": []},
            },
            {
                "name": "get_weather_forecast",
                "description": "Get weather forecast for Rome",
                "input_schema": {"type": "object", "properties": {}, "required": []},
            },
            {
                "name": "get_all_weather",
                "description": "Get both current conditions and forecast",
                "input_schema": {"type": "object", "properties": {}, "required": []},
            },
        ]
        
        return self.mcp_tools

    def get_openrouter_tools(self) -> List[Dict[str, Any]]:
        """Return tools definition in OpenRouter format"""
        return self.openrouter_tools

    async def handle_tool_call(
        self, tool_name: str, arguments: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Handle MCP tool calls"""
        if tool_name == "get_current_weather":
            result = await self.weather_agent.get_current_conditions()
        elif tool_name == "get_weather_forecast":
            result = await self.weather_agent.get_forecast()
        elif tool_name == "get_all_weather":
            result = await self.weather_agent.get_all_weather_data()
        else:
            result = {"error": f"Unknown tool: {tool_name}"}

        return {
            "tool_call_id": f"{tool_name}_response",
            "tool_name": tool_name,
            "result": result,
        }

    def get_tools_definition(self) -> Dict[str, Any]:
        """Return MCP tools definition"""
        return {"version": "1.0", "tools": self.tools}
