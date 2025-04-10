# Use an official Python image
FROM python:3.11-slim

# Install libzbar and other dependencies
RUN apt-get update && apt-get install -y \
    libzbar0 \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port and run the app
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]
