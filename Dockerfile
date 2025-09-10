# Use an official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PORT 8080

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Use gunicorn to run the web server
# The 'exec' form is used to make gunicorn the container's main process (PID 1)
# This allows it to receive signals from Docker, like for shutting down.
# We bind to 0.0.0.0 to accept connections from any IP.
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 main:app