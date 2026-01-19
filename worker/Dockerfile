# ROLE:
# Docker container for background worker.
#
# Executes deployment jobs pulled from queue.

FROM python:3.11-slim

WORKDIR /worker

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt /worker/requirements.txt
RUN pip install --no-cache-dir -r /worker/requirements.txt

COPY app /worker/app

CMD ["python", "-m", "app.worker_main"]
