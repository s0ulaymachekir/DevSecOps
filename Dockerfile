FROM python:3.9-slim
WORKDIR /app
COPY . /app
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
CMD gunicorn --bind 0.0.0.0:5000 app:app
 
