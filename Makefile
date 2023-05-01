DEPLOYMENT_VARS=$(echo \
	$(gcloud secrets versions access latest --secret=lumian_env_file --format='get(payload.data)' | tr '\n' ' ' | base64 -d) \
		| sed 's/ /,/g')
GCLOUD_PLATFORM="linux/amd64"
ARTIFACT_PATH="us-central1-docker.pkg.dev/lumian-ai/lumian-repo"
SQL_CONNECTION="lumian-ai:us-central1:db-dev"

build-synthesis:
	docker build --platform=$(GCLOUD_PLATFORM) -t $(ARTIFACT_PATH)/api-synthesis-amd64 ./api-synthesis

build-api:
	docker build --platform=$(GCLOUD_PLATFORM) -t $(ARTIFACT_PATH)/api-amd64 ./api

build-web:
	docker build --platform=$(GCLOUD_PLATFORM) -t $(ARTIFACT_PATH)/web-amd64 ./web

push-synthesis:
	docker push $(ARTIFACT_PATH)/api-synthesis-amd64

push-api:
	docker push $(ARTIFACT_PATH)/api-amd64

push-web:
	docker push $(ARTIFACT_PATH)/web-amd64

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
	URL_API_SYNTHESIS=$(gcloud run services describe api-synthesis --platform=managed --region=us-central1 --format="value(status.url)")
	gcloud run deploy api \
        --image $(ARTIFACT_PATH)/api-amd64 \
        --platform managed \
        --region us-central1 \
        --allow-unauthenticated \
        --port=8000 \
        --set-env-vars DB_HOST="/cloudsql/$(SQL_CONNECTION)",SYNTHESIS_CORE_BASE_URL=$URL_API_SYNTHESIS,$DEPLOYMENT_VARS  \
        --add-cloudsql-instances $SQL_CONNECTION

deploy-web:
	gcloud run deploy web \
        --image $(ARTIFACT_PATH)/web-amd64 \
        --platform managed \
        --region us-central1 \
        --allow-unauthenticated \
        --port=8002

build: build-synthesis build-api build-web

push: push-synthesis push-api push-web

deploy: deploy-synthesis deploy-api deploy-web

.PHONY: build push
