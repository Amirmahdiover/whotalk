FROM python:3.12

WORKDIR /djangoProjectChatBot/

# Install dependencies
COPY ./requirements.txt ./
RUN pip install -r requirements.txt

# Copy full project after installing dependencies
ADD ./ ./

# Set environment variables required by Django
ENV DJANGO_SETTINGS_MODULE=djangoProjectChatBot.settings
ENV PYTHONUNBUFFERED=1

# Collect static files *after* copying everything
RUN python manage.py collectstatic --noinput

# Start services
ENTRYPOINT ["/bin/sh", "-c", "python manage.py migrate && celery -A djangoProjectChatBot worker --concurrency=4 --prefetch-multiplier=8 --loglevel=info & gunicorn --bind 0.0.0.0:8000 djangoProjectChatBot.wsgi"]
