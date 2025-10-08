#!/bin/sh
 
python manage.py collectstatic --noinput || true
 
python manage.py migrate --skip-checks --verbosity 0
 
python manage.py import_dynamic_models_data --skip-checks
 
# python manage.py createsuperuser --skip-checks
 
# python manage.py runserver 0.0.0.0:8000 --skip-checks

gunicorn 'PIA.wsgi' --bind 0.0.0.0:8000 --workers 3 --threads 4 --log-level info
