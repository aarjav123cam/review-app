export PORT=8080
export PROJECT_ID=dev-setting-264816
export COMMIT_SHA=latest
export IDENTIFIER=twilio-app
export CLOUD_RUN_LOCATION=europe-west2
IMAGE_NAME=twilio-app


cloudbuild: get-secrets build-image
cloudbuild-and-deploy: get-secrets build-image deploy-image

# Step to build the Docker image
build-image:
	podman build -t $(IMAGE_NAME) \
	--build-arg TWILIO_SID=$(TWILIO_SID),TWILIO_AUTH_TOKEN=$(TWILIO_AUTH_TOKEN) \
	..



# Step to run the Docker image
run:
	podman run -p 8080:8080  $(IMAGE_NAME)

# Step to see the output of the running container
logs:
	podman logs -f $(IMAGE_NAME)_container



install-requirements:
	pip install -r requirements.txt

get-secrets:
	@TWILIO_SID=$$(gcloud secrets versions access latest --secret=TWILIO_SID) && \
	TWILIO_AUTH_TOKEN=$$(gcloud secrets versions access latest --secret=TWILIO_AUTH_TOKEN) && \
	export TWILIO_SID && \
	export TWILIO_AUTH_TOKEN


run-server:
	uvicorn app:app --reload

build-image:
	cd ../ && \
	gcloud builds submit \
	--config cloudbuild.yaml \
	--substitutions=COMMIT_SHA=${COMMIT_SHA},\
	_PROJECT_ID=${PROJECT_ID},\
	_IMAGE_NAME=${IDENTIFIER}


deploy-image:
	gcloud run deploy ${IDENTIFIER} \
	--image "europe-docker.pkg.dev/${PROJECT_ID}/docker/${IDENTIFIER}:latest" \
	--region ${CLOUD_RUN_LOCATION} \
	--set-secrets TWILIO_AUTH_TOKEN=TWILIO_AUTH_TOKEN:latest,TWILIO_SID=TWILIO_SID:latest \
	--allow-unauthenticated