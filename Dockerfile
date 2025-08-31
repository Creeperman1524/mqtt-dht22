FROM python:3.9-slim-bullseye AS builder

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /builder

RUN apt-get update && apt-get install -y \
    gcc \
    libgpiod2 \
    libgpiod-dev \
    python3-dev \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --target=/install --no-cache-dir \
	paho-mqtt \
	adafruit-circuitpython-dht \
	RPI.GPIO

FROM python:3.9-slim-bullseye

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
	libgpiod2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /app

ADD dht22.py .

CMD ["python", "-u", "dht22.py"]
