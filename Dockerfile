FROM python:3.10.11-slim

ARG TWILIO_SID
ARG TWILIO_AUTH_TOKEN
ARG GOOGLE_CLIENT_ID
ARG GOOGLE_CLIENT_SECRET
ARG SECRET_KEY

# Use ARG values as environment variables
ENV TWILIO_SID=${TWILIO_SID}
ENV TWILIO_AUTH_TOKEN=${TWILIO_AUTH_TOKEN}
ENV GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
ENV GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}
ENV SECRET_KEY=${SECRET_KEY}


WORKDIR /app
COPY /app  .


# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

ENV PORT=8080

#
## Run app.py when the container launches
##CMD ["uvicorn", "app:app"]
#CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
# Assuming 'run.py' is in the same directory as your Dockerfile
CMD ["python", "run.py"]
