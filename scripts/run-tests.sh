#!/bin/sh

docker-compose run --rm app sh -c "python manage.py test"
docker-compose run --rm app_synthesis sh -c "PYTHONPATH=. pytest tests"
