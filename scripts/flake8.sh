#!/bin/sh

docker-compose run --rm app sh -c "flake8"
docker-compose run --rm app_synthesis sh -c "flake8"
