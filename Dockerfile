FROM python:3.9-slim
WORKDIR /app
COPY . .
# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential=11.1 \
    pkg-config=0.29.2-1 \
    default-libmysqlclient-dev=1.0.0 \
    && rm -rf /var/lib/apt/lists/*
RUN pip install -r requirements.txt
CMD gunicorn --bind 0.0.0.0:5000 app:app
 
