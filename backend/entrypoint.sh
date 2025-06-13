#!/bin/bash

echo "Waiting for postgres..."
while ! nc -z db 5432; do
  sleep 1
done
echo "PostgreSQL started"


python manage.py migrate


python manage.py collectstatic --no-input

echo "Loading ingredients data..."
python manage.py load_ingredients /app/data/ingredients.json || echo "Failed to load ingredients"


python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin')"

echo "Creating test data if not exists..."
python manage.py commands || echo "Failed to create test data"

exec gunicorn foodgram_backend.wsgi:application --bind 0.0.0.0:8000