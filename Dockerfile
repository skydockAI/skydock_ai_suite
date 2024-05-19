# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/go/dockerfile-reference/

# Want to help us make this template better? Share your feedback here: https://forms.gle/ybq9Krt8jtBL3iCk7

ARG PYTHON_VERSION=3.10.12
FROM python:${PYTHON_VERSION}-slim as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into this layer
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Install Graphviz for graph generation
RUN apt-get update && apt-get install -y graphviz

# Copy the source code and required resources into the container.
COPY ./src/. .
COPY ./resources/. .

# Initialize Chainlit
RUN chainlit init

# Copy config file for Chainlit
COPY ./config.toml /app/.chainlit

# Make port available for the Chainlit app.
# Need to match with the value in config.env file
EXPOSE 8000

# Give execute permission to the entrypoint script
RUN chmod +x /app/skydock_ai_suite.sh

# Run the entrypoint script
ENTRYPOINT ["/app/skydock_ai_suite.sh"]
