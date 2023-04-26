# Lumion Interview Synthesizer

Website, REST APIs and Admin interfaces to synthesize interview transcripts

## Setup

1. Create a `.env` file in your project root, copy the variables from `.env.sample`, and change their values.
2. Install [docker](https://docs.docker.com/get-docker/)
3. Build the containers

```
docker-compose build
```

4. Run the services

```
docker-compose up
```

5. (When done) Stop and wind down the containers

```
docker-compose down
```

## Usage

- Website is set up to run on port 8002.
- REST APIs are set up to run on port 8000.
- You can view REST APIs from the `/api/docs/` endpoint.
- You can access the Django admin pages from the `/admin` endpoint.

## Changes

Before pushing your code, be sure to run tests and linting

```
./scripts/run-tests.sh
./scripts/flake8.sh
```
