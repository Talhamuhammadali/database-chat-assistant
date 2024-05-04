# Use a base image with Python
FROM python:3.10.12

# Set up python
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Upadating pip
RUN pip3 install --upgrade pip

# Copy requirements to docker
COPY requirements.txt /requirements.txt
RUN pip3 --no-cache-dir install -r /requirements.txt

# Copy .env file
COPY .env /app/.env

# Set work Directory
WORKDIR /app

# Copy the rest of the application files
COPY . /app

# Expose port for communication
EXPOSE 8080

# Command to run the FastAPI application using uvicorn
CMD ["gunicorn", "-w", "1", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
