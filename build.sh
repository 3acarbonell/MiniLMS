#!/usr/bin/env bash
# Exit on error
set -o errexit

# Convert static asset files
python manage.py collectstatic --no-input

# Apply any outstanding database migrations
python manage.py makemigrations
python manage.py migrate --noinput

# Population
python manage.py populate_users
python manage.py populate_courses