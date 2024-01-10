FROM python:3.10.11-slim

ARG TWILIO_SID
ARG TWILIO_AUTH_TOKEN

# Use ARG values as environment variables
ENV TWILIO_SID=${TWILIO_SID}
ENV TWILIO_AUTH_TOKEN=${TWILIO_AUTH_TOKEN}


WORKDIR /app
COPY /app  .


# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000


# Run app.py when the container launches
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
