FROM mcr.microsoft.com/playwright/python:v1.49.0-noble

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    SPECTER_PAGE="QCGov" \
    SPECTER_INTERVAL=300 \
    SPECTER_MODE="auto"

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and assets
COPY src/ ./src/
COPY main.py .

# Create volume mount target for SQLite database and cookie storage
RUN mkdir -p /app/data

VOLUME ["/app/data"]

ENTRYPOINT ["python", "main.py", "--monitor"]
