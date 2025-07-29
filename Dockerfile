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
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser -u 900 appuser

# Set up application directory
WORKDIR /app
RUN chown appuser:appuser /app

# Copy pyproject.toml for dependency installation
COPY pyproject.toml ./

# Install dependencies without building the package
RUN uv export --no-dev --format requirements-txt > requirements.txt && \
    uv pip install --system -r requirements.txt && \
    rm requirements.txt

# Install Playwright Firefox browser (as non-root for security)
USER appuser
RUN uv run playwright install firefox
USER root

# Copy application files
COPY main.py config.py ./
RUN chown appuser:appuser *.py

# Switch to non-root user and run the application
USER appuser

CMD ["python", "main.py"]