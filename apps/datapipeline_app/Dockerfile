# DATA INGESTION
# Accepts payload from pond sensors, Checks payload content, and Sends payload to database

FROM python:3.12-slim-bookworm

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD ["python", "src/app.py", "--port", "8080"]