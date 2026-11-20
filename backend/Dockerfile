FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

COPY pyproject.toml ./
COPY app ./app
RUN pip install --no-cache-dir .

COPY migrations ./migrations
COPY alembic.ini ./
COPY docker ./docker
RUN chmod +x docker/entrypoint.sh

ENV SCENARIOS_DIR=/app/scenarios
EXPOSE 8000
CMD ["docker/entrypoint.sh"]
