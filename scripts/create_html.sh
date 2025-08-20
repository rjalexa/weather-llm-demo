#!/bin/bash
# Create HTML interface as separate script due to size

cat > ../index.html << 'HTMLEOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weather LLM Demo - Rome IROME8278</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container { max-width: 1200px; margin: 0 auto; }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        
        .main-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        
        @media (max-width: 768px) {
            .main-grid { grid-template-columns: 1fr; }
        }
        
        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .weather-display h2 {
            color: #333;
            margin-bottom: 20px;
        }
        
        .weather-item {
            display: flex;
            justify-content: space-between;
            padding: 10px;
            background: #f7f7f7;
            border-radius: 8px;
            margin-bottom: 10px;
        }
        
        .chat-messages {
            height: 400px;
            overflow-y: auto;
            padding: 20px;
            background: #f9f9f9;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        
        .message {
            margin-bottom: 15px;
            padding: 12px 15px;
            border-radius: 10px;
            max-width: 80%;
        }
        
        .message.user {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            margin-left: auto;
        }
        
        .message.assistant {
            background: white;
            border: 1px solid #e0e0e0;
        }
        
        .chat-input {
            display: flex;
            gap: 10px;
        }
        
        .chat-input input {
            flex: 1;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 25px;
            font-size: 16px;
        }
        
        .chat-input button {
            padding: 12px 25px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
        }
        
        .example-query {
            display: inline-block;
            margin: 5px;
            padding: 5px 10px;
            background: white;
            border: 1px solid #ddd;
            border-radius: 15px;
            cursor: pointer;
            font-size: 14px;
        }
        
        .example-query:hover {
            background: #667eea;
            color: white;
        }
        
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(0,0,0,.1);
            border-radius: 50%;
            border-top-color: #667eea;
            animation: spin 1s ease-in-out infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌤️ Weather LLM Demo</h1>
            <p>Rome Station IROME8278 - Multilingual AI Weather Assistant</p>
        </div>
        
        <div class="main-grid">
            <div class="card">
                <h2>🌡️ Current Conditions</h2>
                <div id="currentWeather">
                    <div class="loading"></div>
                </div>
            </div>
            
            <div class="card">
                <h2>📅 Forecast</h2>
                <div id="forecast">
                    <div class="loading"></div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>💬 Chat with Weather Assistant</h2>
            
            <div style="margin-bottom: 15px;">
                <strong>Example queries (try in any language!):</strong>
                <div>
                    <span class="example-query" onclick="sendExample('Che tempo fa oggi a Roma?')">🇮🇹 Che tempo fa?</span>
                    <span class="example-query" onclick="sendExample('What should I wear today?')">🇬🇧 What to wear?</span>
                    <span class="example-query" onclick="sendExample('Quel temps fait-il?')">🇫🇷 Quel temps?</span>
                    <span class="example-query" onclick="sendExample('¿Necesito paraguas?')">🇪🇸 ¿Paraguas?</span>
                    <span class="example-query" onclick="sendExample('Devo portare lombrello?')">☔ Ombrello?</span>
                </div>
            </div>
            
            <div class="chat-messages" id="chatMessages">
                <div class="message assistant">
                    Ciao! Sono il tuo assistente meteo per Roma. Chiedimi qualsiasi cosa sul tempo! 
                    <br><br>
                    Hello! I'm your weather assistant for Rome. Ask me anything about the weather!
                </div>
            </div>
            
            <div class="chat-input">
                <input type="text" id="chatInput" placeholder="Ask about the weather in any language..." 
                       onkeypress="if(event.key==='Enter') sendMessage()">
                <button onclick="sendMessage()">Send</button>
            </div>
        </div>
    </div>
    
    <script>
        // Fetch and display weather data
        async function loadWeather() {
            try {
                const response = await fetch('/api/weather/all');
                const data = await response.json();
                
                // Display current conditions
                const current = data.current;
                document.getElementById('currentWeather').innerHTML = `
                    <div class="weather-item">
                        <span>Temperature</span>
                        <strong>${current.temperature_c}°C</strong>
                    </div>
                    <div class="weather-item">
                        <span>Feels Like</span>
                        <strong>${current.feels_like_c}°C</strong>
                    </div>
                    <div class="weather-item">
                        <span>Humidity</span>
                        <strong>${current.humidity}%</strong>
                    </div>
                    <div class="weather-item">
                        <span>Wind</span>
                        <strong>${current.wind_kmh} km/h</strong>
                    </div>
                    <div class="weather-item">
                        <span>Conditions</span>
                        <strong>${current.description}</strong>
                    </div>
                `;
                
                // Display forecast
                const forecast = data.forecast;
                document.getElementById('forecast').innerHTML = `
                    <div class="weather-item">
                        <span>Today</span>
                        <strong>${forecast.today.high_c}°C / ${forecast.today.low_c}°C</strong>
                    </div>
                    <div class="weather-item">
                        <span>Tomorrow</span>
                        <strong>${forecast.tomorrow.high_c}°C / ${forecast.tomorrow.low_c}°C</strong>
                    </div>
                    <div class="weather-item">
                        <span>Rain Chance Today</span>
                        <strong>${forecast.today.precipitation_chance}%</strong>
                    </div>
                `;
            } catch (error) {
                console.error('Error loading weather:', error);
            }
        }
        
        // Chat functionality
        async function sendMessage() {
            const input = document.getElementById('chatInput');
            const message = input.value.trim();
            if (!message) return;
            
            // Add user message
            addMessage(message, 'user');
            input.value = '';
            
            // Show loading
            const loadingId = addMessage('<div class="loading"></div>', 'assistant');
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        message: message,
                        include_forecast: true
                    })
                });
                
                const data = await response.json();
                
                // Remove loading and add response
                document.getElementById(loadingId).remove();
                addMessage(data.response, 'assistant');
                
            } catch (error) {
                document.getElementById(loadingId).remove();
                addMessage('Error: Could not get response', 'assistant');
            }
        }
        
        function sendExample(text) {
            document.getElementById('chatInput').value = text;
            sendMessage();
        }
        
        function addMessage(text, type) {
            const messagesDiv = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            const messageId = 'msg-' + Date.now();
            messageDiv.id = messageId;
            messageDiv.className = 'message ' + type;
            messageDiv.innerHTML = text;
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
            return messageId;
        }
        
        // Load weather on page load
        loadWeather();
        setInterval(loadWeather, 60000); // Refresh every minute
    </script>
</body>
</html>
HTMLEOF

echo "✅ HTML interface created"
