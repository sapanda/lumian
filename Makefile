DEPLOYMENT_VARS=$(shell gcloud secrets versions access latest --secret=lumian_env_file --format='get(payload.data)' | base64 -d | tr '\n ' ', ' | tr -s ',')
GCLOUD_PLATFORM=linux/amd64
ARTIFACT_PATH=us-central1-docker.pkg.dev/lumian-ai/lumian-repo
SQL_CONNECTION=lumian-ai:us-central1:db-dev
URL_API="https://api-exhuonkrba-uc.a.run.app"
URL_API_SYNTHESIS="https://api-synthesis-exhuonkrba-uc.a.run.app"


#################################
# Build
#################################
.PHONY: build

build-synthesis:
	docker build --platform=$(GCLOUD_PLATFORM) -t $(ARTIFACT_PATH)/api-synthesis-amd64 ./api-synthesis

build-api:
	docker build --platform=$(GCLOUD_PLATFORM) -t $(ARTIFACT_PATH)/api-amd64 ./api

build-web:
	docker build --platform=$(GCLOUD_PLATFORM) -t $(ARTIFACT_PATH)/web-amd64 ./web

build: build-synthesis build-api build-web


#################################
# Push
#################################
.PHONY: push

push-synthesis:
	docker push $(ARTIFACT_PATH)/api-synthesis-amd64

push-api:
	docker push $(ARTIFACT_PATH)/api-amd64

push-web:
	docker push $(ARTIFACT_PATH)/web-amd64

push: push-synthesis push-api push-web


#################################
# Deploy
#################################
.PHONY: deploy

deploy-synthesis:
	gcloud run deploy api-synthesis \
        --image $(ARTIFACT_PATH)/api-synthesis-amd64 \
        --platform managed \
        --region us-central1 \
        --allow-unauthenticated \
        --port=8001 \
        --set-env-vars DB_HOST="/cloudsql/$(SQL_CONNECTION)",$(DEPLOYMENT_VARS) \
        --add-cloudsql-instances $(SQL_CONNECTION)

deploy-api:
	gcloud run deploy api \
        --image $(ARTIFACT_PATH)/api-amd64 \
        --platform managed \
        --region us-central1 \
        --allow-unauthenticated \
        --port=8000 \
        --set-env-vars DB_HOST="/cloudsql/$(SQL_CONNECTION)",CSRF_TRUSTED_ORIGINS=$(URL_API),SYNTHESIS_URL=$(URL_API_SYNTHESIS),$(DEPLOYMENT_VARS) \
        --add-cloudsql-instances $(SQL_CONNECTION);

deploy-web:
	gcloud run deploy web \
        --image $(ARTIFACT_PATH)/web-amd64 \
        --platform managed \
        --region us-central1 \
        --allow-unauthenticated \
        --port=8002

deploy: deploy-synthesis deploy-api deploy-web


#################################
# Convenience Recipes
#################################
synthesis: build-synthesis push-synthesis deploy-synthesis

api: build-api push-api deploy-api

web: build-web push-web deploy-web
