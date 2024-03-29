# Lumian Deployment Instructions

## Development Server

### Access

The dev server is running on a Google Compute Engine instance. You can ssh into the instance using the command.

```
gcloud compute ssh --zone "us-central1-a" "deployment-test" --project "lumian-ai"
```

Run as superuser and cd to the project directory.

```
su
cd Repos/lumian
```

### Environment

The .env file has already been set up. The `.env.deploy.sample` file shows all the environment variables that need to be set.

### Deployment

The deployment docker-compose is `docker-compose-deploy.yml`. To run any docker-compose commands, you will need to specify this file as the input as shown below.

⚠️ WARNING: If you accidentally build or deploy the standard docker-compose file, your containers may end up in a bad state and you may need to do a clean build.

The deployment process is generally simple: wind down the existing services, update the code, do a rebuild and spin them back up.

```
docker-compose -f docker-compose-deploy.yml down
git pull origin
docker-compose -f docker-compose-deploy.yml build
docker-compose -f docker-compose-deploy.yml up
```

For convenience, the `~/.bashrc` has a few aliases that you can use to simplify the commands:

```
alias dcbf="docker-compose -f docker-compose-deploy.yml build"
alias dcuf="docker-compose -f docker-compose-deploy.yml up"
alias dcdf="docker-compose -f docker-compose-deploy.yml down"
```

### SSL Certificates

The SSL certs have been generated by following [this guide](https://mindsers.blog/post/https-using-nginx-certbot-docker/). Certificates have already been created and are stored in the project `certbot` folder. However we will need to update them every 90 days using the command below. Certificate renewal notices are currently being sent to robin@lumian.ai.

```
docker-compose -f docker-compose-deploy.yml run --rm certbot renew
```

### GCP Service Accounts

The following GCP service account credentials are needed. They are already set up on the server:

1. Used by Django API service to interact with GCP. Place it in the location denoted by the `GCLOUD_SECRETS_PATH` env var.
2. Used by docker-compose-deploy to log events to GCP. Place it in the located denoted by the `GOOGLE_APPLICATION_CREDENTIALS` env var.
