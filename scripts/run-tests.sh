#!/bin/sh

docker-compose run --rm api sh -c "python manage.py test"
