# Product Checker

[![Lint](https://github.com/axkng/product-checker/actions/workflows/lint.yml/badge.svg)](https://github.com/axkng/product-checker/actions/workflows/lint.yml)
[![Docker Build](https://github.com/axkng/product-checker/actions/workflows/docker.yml/badge.svg)](https://github.com/axkng/product-checker/actions/workflows/docker.yml)

A lightweight Python tool to monitor specific values on websites via scraping. Sends Telegram notifications when monitored values are no longer present on the page.

## 🚀 Quick Start

### Using Docker Compose (Recommended)

1. Create your configuration file:
   ```bash
   cp config.example.json config.json
   # Edit config.json with your Telegram credentials and products
   ```

2. Run with Docker Compose:
   ```bash
   docker-compose up -d
   ```

### Using Docker

1. Pull the latest image:
   ```bash
   docker pull ghcr.io/axkng/product-checker:latest
   ```

2. Run the container:
   ```bash
   docker run -d \
     --name product-checker \
     --restart unless-stopped \
     -v "$(pwd)/config.json:/app/config.json:ro" \
     ghcr.io/axkng/product-checker:latest
   ```

### Running Locally

1. Clone the repository:
   ```bash
   git clone https://github.com/axkng/product-checker.git
   cd product-checker
   ```

2. Install dependencies and run:
   ```bash
   uv sync
   uv run python main.py
   ```

## 📋 Features

- Monitors specific values on multiple websites via JSON config
- Scrapes websites using HTTP requests with Firefox user agent
- Telegram notifications when monitored values change or disappear
- Simple Python implementation with minimal dependencies
- Error logging with timestamps
- Runs continuously in Docker container
- Easy to customize and extend

## ⚙️ Configuration

Create a `config.json` file based on `config.example.json`:

```json
{
  "telegram": "YOUR_BOT_TOKEN:YOUR_CHAT_ID",
  "interval": 60,
  "timeout": 5,
  "product": [
    {
      "name": "Product A",
      "url": "https://example.com/product",
      "value": "1.599"
    }
  ]
}
```

### Configuration Options

- `telegram`: Your Telegram bot token and chat ID (format: `token:chat_id`)
- `interval`: Check interval in seconds  
- `timeout`: Request timeout in seconds (optional, defaults to 5)
- `product`: Array of websites to monitor
  - `name`: Display name for what you're monitoring
  - `url`: Full URL to the page to monitor
  - `value`: Exact text/value to look for on the page

### Requirements

- Python 3.11+
- `uv` package manager
- Dependencies managed via `pyproject.toml`

## 🔧 Development

### Local Development

```bash
uv sync --dev
uv run python main.py
```

### Linting

```bash
# Check code style
uv run ruff check .

# Fix auto-fixable issues
uv run ruff check --fix .

# Format code
uv run ruff format .
```

### Docker Development

```bash
docker build -t product-checker .
docker run -v "$(pwd)/config.json:/app/config.json" product-checker
```

## 📦 Container Registry

Pre-built images are available at:
- `ghcr.io/axkng/product-checker:latest`

## 📝 License

This project is open source and available under the MIT License.
