FROM python:3.12-slim-bullseye

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    unzip && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY scripts/ ./scripts/

COPY db-requirements.txt .

RUN pip install -r db-requirements.txt

CMD ["/bin/bash", "./scripts/dataset_download.sh"]