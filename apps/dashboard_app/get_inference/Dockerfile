# INFERENCE RETRIEVAL
# Requests inference from inference pipeline to display in the dashboard

FROM python:3.12-slim-bookworm

WORKDIR /app

# Copy requirements first
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Create the data directory where the PVC will be mounted
RUN mkdir -p /app/data

RUN chmod 777 /app/data

# Copy entire project
COPY . .