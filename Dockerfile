FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV SECRET_KEY="change_me" \
    APP_EMAIL="admin@example.com" \
    APP_PASSWORD="admin" \
    APP_NAME="Admin User" \
    WORDPRESS_BASE_URL="https://www.your-site-url.com/wp-json/wp/v2" \
    WORDPRESS_USERNAME="wordpress_account_username" \
    WORDPRESS_API_KEY="wordpress_application_password" \
    SQLALCHEMY_DATABASE_URL="sqlite:///./db/contentforge.db" \
    CORS_ORIGINS="https://www.your-first-origin.com,https://www.your-second-origin.com"

EXPOSE 8000

ENV PYTHONPATH=/app

RUN mkdir -p /app/db && chmod -R 777 /app/db

CMD ["sh", "-c", "alembic upgrade head && python scripts/create_user.py && uvicorn main:app --host 0.0.0.0 --port 8000"]
