#!/bin/bash
echo "🚀 Bootstrapping WebDesign Academy..."

# Activate venv
source venv/bin/activate

# Install missing packages
pip install python-dateutil django-cors-headers

# Make migrations
python manage.py makemigrations accounts
python manage.py makemigrations courses
python manage.py makemigrations subscriptions
python manage.py makemigrations progress
python manage.py makemigrations playground
python manage.py makemigrations projects
python manage.py makemigrations dashboard
python manage.py makemigrations community

# Migrate
python manage.py migrate

# Create superuser
python manage.py createsuperuser

echo "✅ Done! Run 'python manage.py runserver' to start."