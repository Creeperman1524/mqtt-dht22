FROM python:3.9-slim

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libgpiod2 \
    libgpiod-dev \
    python3-dev \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install paho-mqtt adafruit-circuitpython-dht RPI.GPIO

ADD dht22.py .

CMD ["python", "-u", "dht22.py"]
