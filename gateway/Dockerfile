# Build context is the repo root (see docker-compose.yml) so this can pull in
# common/, static/, and schema.sql alongside its own code.
FROM python:3.11-slim

WORKDIR /app
ENV PYTHONPATH=/app

COPY gateway/requirements.txt gateway/requirements.txt
RUN pip install --no-cache-dir -r gateway/requirements.txt

COPY common common
COPY gateway gateway
COPY static gateway/static
COPY schema.sql schema.sql

WORKDIR /app/gateway
CMD ["sh", "entrypoint.sh"]
