FROM python:3.12-slim-bookworm

COPY ./send-request.py .

RUN pip install requests

CMD ["python3", "./send-request.py"]