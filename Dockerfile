# Use a fuller Debian-based Python image for easier dependency handling
FROM python:3.11-bullseye

# Install zbar and other essential libraries
RUN apt-get update && apt-get install -y \
    libzbar0 \
    libzbar-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy all project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the correct port (match Render settings)
EXPOSE 10000

# Run the app with Gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]
