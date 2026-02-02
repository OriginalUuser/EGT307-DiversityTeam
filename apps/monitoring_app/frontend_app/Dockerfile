# FRONTEND MONITORING APPLICATION
# Solely the Evidently dashboard and report UI

FROM python:3.12-slim-bookworm

COPY . .

ENV WORKSPACE_DIR="/vol/workspace"

RUN pip install --no-cache-dir evidently==0.7.20
RUN python3 ./setup_ws.py

EXPOSE 8000

ENTRYPOINT [ "evidently", "ui" ]
CMD [ "--workspace", "/vol/workspace", "--host", "0.0.0.0", "--port", "8000" ]