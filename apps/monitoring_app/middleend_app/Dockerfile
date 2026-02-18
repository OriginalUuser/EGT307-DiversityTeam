FROM python:3.12-slim-bookworm

COPY ./requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Database env variables
ENV DATABASE_USER=""
ENV DATABASE_NAME="sensor-db"
ENV POSTGRES_PASS=""
ENV DATABASE_HOST="sensor-db-ha-rw.database-ns"
ENV DATABASE_PORT="5432"

ENTRYPOINT [ "uvicorn" ]
CMD [ "src.app:app", "--host", "0.0.0.0", "--port", "8001" ]