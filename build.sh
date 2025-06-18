#!/bin/bash

docker image rm dht22-mqtt
docker build -t dht22-mqtt .
