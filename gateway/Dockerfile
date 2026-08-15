# Build context is the repo root (see docker-compose.yml) so this can pull in
# gateway/, services/, static/, and schema.sql. Runs from the repo root so
# relative paths (static/, schema.sql) resolve the same way they do on Vercel.
FROM python:3.11-slim

WORKDIR /app
ENV PYTHONPATH=/app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY gateway gateway
COPY services services
COPY static static
COPY schema.sql schema.sql

CMD ["sh", "gateway/entrypoint.sh"]
