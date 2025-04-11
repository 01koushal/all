FROM python:3.10-slim

# System packages
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    zbar-tools \
    libzbar0 \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libxss1 \
    libappindicator1 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libasound2 \
    curl \
    wget \
    fonts-liberation \
    && apt-get clean

ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# App setup
WORKDIR /app
COPY . /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8080

CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
