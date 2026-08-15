# Build context is the repo root (see docker-compose.yml) so this can pull in common/.
FROM python:3.11-slim

WORKDIR /app
ENV PYTHONPATH=/app

COPY services/teaching_service/requirements.txt services/teaching_service/requirements.txt
RUN pip install --no-cache-dir -r services/teaching_service/requirements.txt

COPY common common
COPY services/teaching_service services/teaching_service
COPY generate_courses.py generate_courses.py
COPY schema.sql schema.sql

CMD ["python", "services/teaching_service/worker.py"]
