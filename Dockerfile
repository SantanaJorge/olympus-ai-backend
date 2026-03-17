FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if any needed (e.g. for psycopg2)
# libpq-dev is often needed for psycopg2
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose the port the app runs on
EXPOSE 6000

ENV PYTHONPATH=/app

CMD ["python", "main.py"]
