# Use Python slim for smaller image size
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Install system dependencies (for psycopg2 etc.)
RUN apt-get update && apt-get install -y build-essential libpq-dev && apt-get clean

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire app source code
COPY . .

# Expose the FastAPI port
EXPOSE 8000

# Start the FastAPI server using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
