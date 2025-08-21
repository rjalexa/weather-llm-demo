import httpx
from typing import Dict, Any, List, Optional


class OpenRouterClient:
    """Client for OpenRouter API with Italian weather responses"""

    def __init__(self, api_key_file: str = ".openrouter_api_key"):
        self.api_key = self._load_api_key(api_key_file)
        self.base_url = "https://openrouter.ai/api/v1"
        import os
        self.model = os.getenv("TOOL_CALLING_OPENROUTER_LLM_MODEL", "openai/gpt-3.5-turbo")  # Configurable model with fallback

    def _load_api_key(self, api_key_file: str) -> str:
        """Load API key from file"""
        try:
            with open(api_key_file, "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            print(f"⚠️  {api_key_file} not found. Running in demo mode.")
            return "demo_key"

    async def create_completion(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        """Create completion with weather context"""

        if self.api_key == "demo_key":
            return self._create_demo_response(messages)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "Weather LLM Demo",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1024,
        }

        # Add tools to payload if provided
        if tools is not None:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30.0,
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    return self._create_demo_response(messages)

        except Exception as e:
            print(f"Using demo mode due to: {e}")
            return self._create_demo_response(messages)

    def _create_demo_response(
        self, messages: List[Dict]
    ) -> Dict[str, Any]:
        """Create a generic demo response for when the API key is not available."""
        return {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "Welcome! The app is in demo mode. Please provide an OpenRouter API key to get live weather information.",
                    }
                }
            ]
        }

