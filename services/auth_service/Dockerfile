# Build context is the repo root (see docker-compose.yml) so this can pull in common/.
FROM python:3.11-slim

WORKDIR /app
ENV PYTHONPATH=/app

COPY services/auth_service/requirements.txt services/auth_service/requirements.txt
RUN pip install --no-cache-dir -r services/auth_service/requirements.txt

COPY common common
COPY services/auth_service services/auth_service

CMD ["python", "services/auth_service/worker.py"]
