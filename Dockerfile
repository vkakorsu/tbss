# Base image
FROM python:3.12-slim

# Prevent Python from writing .pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# System deps (build tools, libpq if you switch to Postgres later)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (better layer caching)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Expose port (Gunicorn will bind here)
EXPOSE 8000

# Collect static files (safe even if STATIC_ROOT is empty)
RUN python manage.py collectstatic --noinput

# Default environment (override in docker run or compose)
ENV DJANGO_SETTINGS_MODULE=config.settings.base

# Run the Django app with Gunicorn
# NOTE: Ensure `gunicorn` is in your requirements.txt
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
