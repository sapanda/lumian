# Transcript Synthesis APIs
REST APIs and Admin interfaces to synthesize interview transcripts

## Setup
1. Create a `.env` file in your project root with the following OpenAI secrets:
```
OPENAI_ORG_ID=<your-org-id>
OPENAI_API_KEY=<your-api-key>
```
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
* You can access rest APIs from the `/api/docs/` endpoint.
* You can access the Django admin pages from the `/admin` endpoint.

## Changes
Before pushing your code, be sure to run tests and linting
```
docker-compose run --rm app sh -c "python manage.py test && flake8"
```
