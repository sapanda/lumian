#!/bin/sh

set -e

python manage.py wait_for_db
python manage.py migrate

if [ $DEPLOY_MODE != "local" ]; then
    python manage.py collectstatic --noinput
fi

if [ $DEPLOY_MODE = "dev" ] || [ $DEPLOY_MODE = "prod" ]; then
    uwsgi --socket :9000 --workers 4 --master --enable-threads --module app.wsgi
else
    python manage.py runserver 0.0.0.0:8000
fi
