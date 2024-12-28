FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV SECRET_KEY="change_me" \
    SQLALCHEMY_DATABASE_URL="postgresql://username:password@localhost/dbname" \
    CORS_ORIGINS="https://www.your-first-origin.com,https://www.your-second-origin.com"

EXPOSE 8000

ENV PYTHONPATH=/app

RUN mkdir -p /app/db && chmod -R 777 /app/db

CMD ["sh", "-c", "alembic upgrade head && python scripts/initialize_settings.py && uvicorn main:app --host 0.0.0.0 --port 8000"]
