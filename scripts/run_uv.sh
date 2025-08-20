#!/bin/bash

echo "🚀 Weather LLM Demo Launcher (UV Edition)"
echo "=========================================="

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ UV is not installed!"
    echo "📦 Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Check for API key
if [ ! -f "../.openrouter_api_key" ]; then
    echo "⚠️  No .openrouter_api_key file found!"
    echo "📝 Creating from example..."
    echo "demo_key" > ../.openrouter_api_key
    echo "⚠️  Please edit ../.openrouter_api_key with your actual API key"
    echo "   Running in DEMO MODE for now..."
    echo ""
fi

# Start the server using uv run
echo "🌤️  Starting Weather LLM Demo Server..."
echo "📍 Station: Rome IROME8278"
echo "🔗 Opening http://localhost:8000"
echo ""

# Run with uv
uv run python -m weather_llm_demo.main
