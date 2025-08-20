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
        tool_results: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Create completion with weather context"""

        if self.api_key == "demo_key":
            return self._create_demo_response(messages, tool_results)

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
                    return self._create_demo_response(messages, tool_results)

        except Exception as e:
            print(f"Using demo mode due to: {e}")
            return self._create_demo_response(messages, tool_results)

    def _create_demo_response(
        self, messages: List[Dict], tool_results: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Create intelligent demo responses based on weather conditions"""
        last_message = messages[-1]["content"] if messages else ""

        # Language detection
        lang_indicators = {
            "it": ["ciao", "come", "che", "oggi", "tempo", "fa", "piove"],
            "fr": ["bonjour", "quel", "fait", "temps", "aujourd"],
            "es": ["hola", "qué", "hace", "tiempo", "llueve"],
            "de": ["hallo", "wie", "wetter", "heute", "regnet"],
        }

        language = "en"
        for lang, words in lang_indicators.items():
            if any(word in last_message.lower() for word in words):
                language = lang
                break

        # Generate weather-aware response
        if tool_results and "current" in tool_results:
            temp = tool_results["current"].get("temperature_c", 22)
            humidity = tool_results["current"].get("humidity", 60)
            conditions = tool_results["current"].get("description", "Clear")

            responses = {
                "it": self._generate_italian_response(
                    temp, humidity, conditions, tool_results
                ),
                "fr": self._generate_french_response(temp, humidity, conditions),
                "es": self._generate_spanish_response(temp, humidity, conditions),
                "de": self._generate_german_response(temp, humidity, conditions),
                "en": self._generate_english_response(temp, humidity, conditions),
            }

            response = responses.get(language, responses["en"])
        else:
            greetings = {
                "it": "Benvenuto! Sono il tuo assistente meteo per Roma. Come posso aiutarti?",
                "fr": "Bienvenue! Je suis votre assistant météo pour Rome. Comment puis-je vous aider?",
                "es": "¡Bienvenido! Soy tu asistente meteorológico para Roma. ¿Cómo puedo ayudarte?",
                "de": "Willkommen! Ich bin Ihr Wetterassistent für Rom. Wie kann ich Ihnen helfen?",
                "en": "Welcome! I'm your weather assistant for Rome. How can I help you?",
            }
            response = greetings.get(language, greetings["en"])

        return {"choices": [{"message": {"role": "assistant", "content": response}}]}

    def _generate_italian_response(self, temp, humidity, conditions, tool_results):
        """Generate detailed Italian weather response"""
        response = "📍 **Roma - Stazione IROME8278**\n\n"
        response += f"🌡️ Temperatura attuale: **{temp}°C**\n"
        response += f"💧 Umidità: {humidity}%\n"
        response += f"☁️ Condizioni: {conditions}\n\n"

        if temp > 30:
            response += "🔥 **Fa molto caldo!** Ecco i miei consigli:\n"
            response += "• Indossa abiti leggeri e di colore chiaro\n"
            response += "• Bevi almeno 2 litri d'acqua durante la giornata\n"
            response += "• Evita di uscire tra le 12:00 e le 16:00\n"
            response += "• Usa la protezione solare SPF 30+\n"
            response += "• Cerca luoghi con aria condizionata\n"
        elif temp < 16:
            response += "❄️ **Fa fresco!** Ti consiglio di:\n"
            response += "• Indossare una giacca o un maglione\n"
            response += "• Portare con te una sciarpa leggera\n"
            response += "• Bere bevande calde per scaldarti\n"
        elif "rain" in conditions.lower() or "pioggia" in conditions.lower():
            response += "🌧️ **Possibilità di pioggia!**\n"
            response += "• Non dimenticare l'ombrello ☂️\n"
            response += "• Indossa scarpe impermeabili\n"
            response += "• Guida con prudenza se devi spostarti\n"
        else:
            response += "✨ **Giornata piacevole!**\n"
            response += "• Perfetta per una passeggiata\n"
            response += "• Goditi il bel tempo romano!\n"

        if "forecast" in tool_results:
            forecast = tool_results["forecast"]
            response += "\n📅 **Previsioni:**\n"
            response += f"Oggi: Max {forecast['today']['high_c']}°C, Min {forecast['today']['low_c']}°C\n"
            response += f"Domani: Max {forecast['tomorrow']['high_c']}°C, Min {forecast['tomorrow']['low_c']}°C"

        return response

    def _generate_french_response(self, temp, humidity, conditions):
        if temp > 30:
            return f"Il fait actuellement {temp}°C à Rome. Très chaud! N'oubliez pas de vous hydrater et de porter des vêtements légers."
        elif temp < 16:
            return f"Il fait {temp}°C à Rome. Il fait frais, je vous conseille de bien vous couvrir."
        else:
            return f"Il fait {temp}°C à Rome avec {conditions}. Le temps est agréable!"

    def _generate_spanish_response(self, temp, humidity, conditions):
        if temp > 30:
            return f"La temperatura actual en Roma es {temp}°C. ¡Hace mucho calor! Recuerda hidratarte bien y usar ropa ligera."
        elif temp < 16:
            return f"La temperatura es {temp}°C. Hace fresco, te recomiendo abrigarte bien."
        else:
            return f"Hay {temp}°C en Roma con {conditions}. ¡El tiempo está agradable!"

    def _generate_german_response(self, temp, humidity, conditions):
        if temp > 30:
            return f"Es ist derzeit {temp}°C in Rom. Sehr heiß! Denken Sie daran, viel zu trinken und leichte Kleidung zu tragen."
        elif temp < 16:
            return f"Es ist {temp}°C in Rom. Es ist kühl, ich empfehle warme Kleidung."
        else:
            return f"Es sind {temp}°C in Rom mit {conditions}. Das Wetter ist angenehm!"

    def _generate_english_response(self, temp, humidity, conditions):
        if temp > 30:
            return f"Current temperature in Rome is {temp}°C. Very hot! Remember to stay hydrated and wear light clothes."
        elif temp < 16:
            return (
                f"Temperature is {temp}°C. It's cool, I recommend wearing warm clothes."
            )
        else:
            return f"It's {temp}°C in Rome with {conditions}. Pleasant weather!"
