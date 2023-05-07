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

# Setting up ngrok locally

## Installation

- Visit the official ngrok website and download ngrok: https://ngrok.com/download 
- Create a new account or login to your existing account at https://dashboard.ngrok.com/
- Copy your authentication token from the dashboard: https://dashboard.ngrok.com/get-started/your-authtoken
- Set the authentication token locally by running the following command and replacing <token> with your copied token:

``` ngrok config add-authtoken <token>
```

## Usage

- Start the ngrok server locally by running the following command :
```  ngrok http 127.0.0.1:8000 
```
- Copy the generated URL from the ngrok output.
- Paste the generated URL in the .env file under the DJANGO_ALLOWED_HOSTS variable.
- Use the generated URL to create a new webhook in Recall AI dashboard: https://api.recall.ai/dashboard/webhooks/