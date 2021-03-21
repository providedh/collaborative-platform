#!/bin/bash
cp src/collaborative_platform/collaborative_platform/settings_template.py src/collaborative_platform/collaborative_platform/settings.py
cat /secrets/secrets.py >> src/collaborative_platform/collaborative_platform/settings.py

cp -rf /code/* /app
cd /app

python src/collaborative_platform/manage.py makemigrations
python src/collaborative_platform/manage.py migrate
python src/collaborative_platform/manage.py loaddata core_initial.json
rm -rf /app/static/*
python src/collaborative_platform/manage.py collectstatic
cd src/collaborative_platform/
daphne -p 8081 collaborative_platform.asgi:application &
uwsgi uwsgi.ini
