#!/bin/sh

docker-compose run --rm api sh -c "flake8"
docker-compose run --rm api_synthesis sh -c "flake8"
