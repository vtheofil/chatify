
FROM python:3.11-slim


WORKDIR /app

# Install system dependencies (for psycopg2 etc.)
RUN apt-get update && apt-get install -y build-essential libpq-dev && apt-get clean


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY . .

# Expose the FastAPI port
EXPOSE 8000


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
