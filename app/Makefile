export PORT=8080
export PROJECT_ID=dev-setting-264816
export COMMIT_SHA=latest
export IDENTIFIER=twilio-app
export CLOUD_RUN_LOCATION=europe-west2
IMAGE_NAME=twilio-app

localbuild: get-secrets local-build-image run
cloudbuild: get-secrets build-image
cloudbuild-and-deploy: get-secrets build-image deploy-image

# Step to build the Docker image
local-build-image:
	podman build -t $(IMAGE_NAME) \
	--build-arg TWILIO_SID=$(TWILIO_SID),TWILIO_AUTH_TOKEN=$(TWILIO_AUTH_TOKEN),GOOGLE_CLIENT_ID=$(GOOGLE_CLIENT_ID),GOOGLE_CLIENT_SECRET=$(GOOGLE_CLIENT_SECRET),SECRET_KEY=$(SECRET_KEY),SF_ID=$(SF_ID),SF_SECRET=$(SF_SECRET),WIX_CLIENT_ID=$(WIX_CLIENT_ID),WIX_CLIENT_SECRET=$(WIX_CLIENT_SECRET) \
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
	GOOGLE_CLIENT_ID=$$(gcloud secrets versions access latest --secret=GOOGLE_CLIENT_ID) && \
	GOOGLE_CLIENT_SECRET=$$(gcloud secrets versions access latest --secret=GOOGLE_CLIENT_SECRET) && \
	SECRET_KEY=$$(gcloud secrets versions access latest --secret=SECRET_KEY) && \
	SF_ID=$$(gcloud secrets versions access latest --secret=SF_ID) && \
	SF_SECRET=$$(gcloud secrets versions access latest --secret=SF_SECRET) && \
	WIX_CLIENT_ID=$$(gcloud secrets versions access latest --secret=WIX_CLIENT_ID) && \
	WIX_CLIENT_SECRET=$$(gcloud secrets versions access latest --secret=WIX_CLIENT_SECRET) && \
	export TWILIO_SID && \
	export TWILIO_AUTH_TOKEN && \
	export GOOGLE_CLIENT_ID && \
	export GOOGLE_CLIENT_SECRET && \
	export SECRET_KEY && \
	export SF_ID && \
	export SF_SECRET && \
	export WIX_CLIENT_ID && \
	export WIX_CLIENT_SECRET


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
	--set-secrets TWILIO_AUTH_TOKEN=TWILIO_AUTH_TOKEN:latest,TWILIO_SID=TWILIO_SID:latest,GOOGLE_CLIENT_ID=GOOGLE_CLIENT_ID:latest,GOOGLE_CLIENT_SECRET=GOOGLE_CLIENT_SECRET:latest,SECRET_KEY=SECRET_KEY:latest,SF_ID=SF_ID:latest,SF_SECRET=SF_SECRET:latest,WIX_CLIENT_ID=WIX_CLIENT_ID:latest,WIX_CLIENT_SECRET=WIX_CLIENT_SECRET:latest \
	--allow-unauthenticated