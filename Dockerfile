# Dockerfile
# Base image with Python and pip
FROM python:3.11-slim-buster

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY pyproject.toml poetry.lock ./
RUN pip install poetry
# Add PostgreSQL development libraries
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copy the app code into the container
COPY . .

# Expose port for FastAPI
EXPOSE 8000

# Default command to start the FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
