# DATA VISUALISATION
# Retreives Data from Database and visualises them using meaningful graphs

FROM python:3.12-slim-bookworm

WORKDIR /app

# Copy requirements first
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . .

# Expose Kubernetes port
EXPOSE 8080

