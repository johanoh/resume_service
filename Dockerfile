# Use official Python image as a base
FROM python:3.12.8-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Django’s default port
EXPOSE 8000

# Start Django with Gunicorn
CMD ["sh", "-c", "python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:8000 resume_service.wsgi:application"]
