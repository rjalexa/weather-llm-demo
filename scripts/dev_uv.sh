#!/bin/bash

echo "🔧 Weather LLM Demo - Development Mode (UV)"
echo "==========================================="

# Check for uv
if ! command -v uv &> /dev/null; then
    echo "❌ UV is not installed!"
    exit 1
fi

# Run with auto-reload for development
echo "🔄 Starting with auto-reload..."
echo "📍 http://localhost:8000"
echo ""

uv run uvicorn weather_llm_demo.main:app --reload --host 0.0.0.0 --port 8000
