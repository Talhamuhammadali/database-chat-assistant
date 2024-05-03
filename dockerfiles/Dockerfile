# Set up python
FROM python:3.10.12
# Set work Directory
WORKDIR /app
# Install vllm and gunicorn
RUN pip install vllm gunicorn
# Copy requirements  to docker
COPY . ./requirements.txt 
# Install requirements in container
RUN pip install -r requirements.txt
# Copy app
COPY . .
# copy envirnmoment credentials 
COPY . ./.env

# Port for communication
EXPOSE 8080
# Command to runthe FastAPI application using gunicorn app.main:app --reload
CMD [ "gunicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080" ]

