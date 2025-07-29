FROM python:3.13-slim

# Install system dependencies for Playwright and uv
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    libnss3 \
    libnspr4 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libgtk-3-0 \
    libgbm1 \
    libasound2 \
    libx11-xcb1 \
    libpci3 \
    libgl1-mesa-glx \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Create non-root user with home directory and cache permissions
RUN groupadd -r appuser && useradd -r -g appuser -u 900 -m appuser && \
    mkdir -p /home/appuser/.cache && \
    chown -R appuser:appuser /home/appuser

# Set up application directory
WORKDIR /app
RUN chown appuser:appuser /app

# Copy pyproject.toml for dependency installation
COPY pyproject.toml ./

# Install dependencies without building the package
RUN uv export --no-dev --format requirements-txt > requirements.txt && \
    uv pip install --system -r requirements.txt && \
    rm requirements.txt

# Set Playwright browsers path and install Firefox
ENV PLAYWRIGHT_BROWSERS_PATH=/opt/playwright-browsers
ENV PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=true
RUN mkdir -p /opt/playwright-browsers && \
    uv run playwright install firefox && \
    chmod -R 755 /opt/playwright-browsers

# Copy application files
COPY main.py config.py ./
RUN chown appuser:appuser *.py

# Switch to non-root user and run the application
USER appuser

CMD ["python", "main.py"]