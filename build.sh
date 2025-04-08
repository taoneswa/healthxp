#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Running database migrations..."
python manage.py migrate

if [[ $CREATE_SUPERUSER == "true" ]]; then
    echo "Creating superuser..."
    python manage.py createsuperuser --noinput \
        --username $DJANGO_SUPERUSER_USERNAME \
        --email $DJANGO_SUPERUSER_EMAIL
fi