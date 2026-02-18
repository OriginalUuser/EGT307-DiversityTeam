# BACKEND MONITORING APPLICATION
# Deals with calling the training pipeline and performing data drift evaluations

FROM python:3.12-slim-bookworm

WORKDIR /app

COPY ./requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src/app.py ./src/reporting.py ./

# Remote evidently workspace URL
ENV WORKSPACE_DNS="monitoring-front-service.monitoring-ns"
ENV WORKSPACE_PORT="8000"

# Database
ENV DATABASE_USER=""
ENV DATABASE_NAME="sensor-db"
ENV POSTGRES_PASS=""
ENV DATABASE_HOST="sensor-db-ha-rw.database-ns"
ENV DATABASE_PORT="5432"

# Training
ENV TRAINING_DNS="ml-api-service.ml-application-ns"
ENV TRAINING_PORT="80"

ENTRYPOINT [ "procrastinate" ]
CMD ["--app=app.app", "worker"]