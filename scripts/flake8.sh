#!/bin/sh

docker-compose run --rm api sh -c "flake8"
