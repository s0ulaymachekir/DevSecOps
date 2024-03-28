FROM python:3.9-slim
# Create directory for dependencies in /home
RUN mkdir -p /home/dependencies
# Set the working directory
WORKDIR /home/dependencies
# Copy the dependencies to the working directory
COPY requirements.txt .

# Create a new sources.list file with Debian Buster repository
RUN echo "deb http://deb.debian.org/debian buster main" > /etc/apt/sources.list

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*
RUN pip install -r requirements.txt
# Install Node.js
RUN apt-get update && apt-get install -y curl gnupg && \
    curl -fsSL https://deb.nodesource.com/setup_16.x | bash - && \
    apt-get install -y nodejs
WORKDIR /home/app
COPY . .
CMD gunicorn --bind 0.0.0.0:5000 app:app


