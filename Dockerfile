FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

RUN adduser --disabled-password --gecos "" aceest
USER aceest

# Expose the port the app runs on
EXPOSE 5000

# Initialise the DB and start the app using gunicorn for production
CMD ["sh", "-c", "python -c 'from app import init_db; init_db()' && gunicorn --bind 0.0.0.0:5000 app:app"]
