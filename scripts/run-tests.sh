#!/bin/sh

docker-compose run --rm api sh -c "python manage.py test"
docker-compose run --rm api_synthesis sh -c "PYTHONPATH=. pytest tests"
