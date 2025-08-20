# 🌤️ Weather LLM Demo with UV Package Manager

This project uses `uv` for fast, reliable Python dependency management.

## Prerequisites

### Install UV (if not already installed)

```bash
# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv
```

## Quick Start with UV

### 1. Clone and Setup

```bash
# Navigate to project directory
cd weather-llm-demo

# Sync dependencies with uv
uv sync
```

### 2. Configure API Key

```bash
# Create API key file
echo "your-openrouter-api-key" > .openrouter_api_key

# Or run in demo mode without a key
echo "demo_key" > .openrouter_api_key
```

### 3. Run the Application

#### Option A: Using the UV run script
```bash
./run_uv.sh
```

#### Option B: Using Make
```bash
make run
```

#### Option C: Direct UV command
```bash
uv run python main.py
```

#### Option D: Development mode with auto-reload
```bash
./dev_uv.sh
# or
make dev
```

## Available Commands

### Using Make (Recommended)

```bash
make install    # Install/sync dependencies
make run        # Run the application
make dev        # Run with auto-reload
make test       # Run tests
make clean      # Clean temporary files
make docker-build  # Build Docker image
make docker-run    # Run with Docker
```

### Using UV Directly

```bash
# Install dependencies
uv sync

# Run application
uv run python main.py

# Run with uvicorn (development)
uv run uvicorn main:app --reload

# Add a new dependency
uv add package-name

# Remove a dependency
uv remove package-name

# Update dependencies
uv sync --upgrade
```

## Docker Deployment with UV

### Build and Run

```bash
# Using docker-compose with UV-optimized Dockerfile
docker-compose -f docker-compose.uv.yml up --build

# Or using Make
make docker-build
make docker-run
```

## Project Structure

```
weather-llm-demo/
├── pyproject.toml       # UV/Python project configuration
├── uv.lock             # Locked dependencies (auto-generated)
├── .python-version     # Python version for UV
├── main.py             # FastAPI application
├── weather_agent.py    # Weather data scraper
├── mcp_server.py       # MCP protocol implementation
├── openrouter_client.py # OpenRouter API client
├── index.html          # Web interface
├── run_uv.sh          # UV run script
├── dev_uv.sh          # Development run script
├── Makefile           # Convenience commands
└── .openrouter_api_key # API key (create this)
```

## Why UV?

- **⚡ Fast**: 10-100x faster than pip
- **🔒 Reliable**: Built-in lock file support
- **🎯 Precise**: Exact dependency resolution
- **📦 Modern**: Built in Rust, designed for modern Python
- **🔄 Compatible**: Works with existing Python projects

## Troubleshooting

### UV not found
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Dependencies not installing
```bash
# Clean and reinstall
rm -rf .venv uv.lock
uv sync
```

### Port already in use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

## Development Workflow

1. **Add dependencies**:
   ```bash
   uv add fastapi uvicorn
   ```

2. **Add dev dependencies**:
   ```bash
   uv add --dev pytest black ruff
   ```

3. **Update all dependencies**:
   ```bash
   uv sync --upgrade
   ```

4. **Run tests**:
   ```bash
   uv run pytest
   ```

5. **Format code**:
   ```bash
   uv run black .
   uv run ruff check .
   ```

## Environment Variables

Create a `.env` file for configuration:

```env
OPENROUTER_API_KEY=your-key-here
HOST=0.0.0.0
PORT=8000
```

## API Endpoints

- `GET /` - Web interface
- `GET /api/weather/current` - Current conditions
- `GET /api/weather/forecast` - Weather forecast
- `POST /api/chat` - Chat with assistant
- `GET /docs` - API documentation

---

Enjoy the blazing fast dependency management with UV! 🚀
