# Set up python
FROM python:3.10.12
# Upadating pip
RUN pip install --upgrade pip
# Copy requirements  to docker
COPY requirements.txt /requirements.txt
RUN pip --no-cache-dir install -r requirements.txt
COPY .env /.env
# Set work Directory
WORKDIR /app
# Copy app
COPY . /app
# Port for communication
EXPOSE 8080
# Command to runthe FastAPI application using gunicorn app.main:app --reload
CMD [ "gunicorn", "-w", "1", "-k", "uvicorn.workers.UvicornWorker","app.main:app", "--host", "0.0.0.0", "--port", "8080" ]

