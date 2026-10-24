FROM python:3.15-slim

WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY alembic.ini .
COPY migrations ./migrations
COPY app ./app

USER nobody
EXPOSE 8000
# Bring the schema up to date, then start the API.
# With several API replicas, run the migration as a separate one-off job instead.
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port 8000"]
