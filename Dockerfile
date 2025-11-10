FROM python:3.11-slim

# Author information
LABEL maintainer="harry"

# Set the working directory inside the container
WORKDIR /app

# Copy dependency file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire Django project into the container
COPY . .

# Expose port 8000 for Gunicorn
EXPOSE 8000

# Start the Django application using Gunicorn
CMD ["gunicorn", "DevOpsDemo.wsgi:application", "--bind", "0.0.0.0:8000"]
