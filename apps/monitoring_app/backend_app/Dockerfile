# BACKEND MONITORING APPLICATION
# Deals with calling the training pipeline and performing data drift evaluations

FROM python:3.12-slim-bookworm

COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Remote evidently workspace URL
ENV WORKSPACE_URL="http://evidently-ui:8000"

ENTRYPOINT [ "uvicorn" ]
CMD [ "src.app:app", "--host", "0.0.0.0", "--port", "8001" ]