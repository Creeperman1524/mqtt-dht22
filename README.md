# mqtt-dht22

This script allows you to collect data from a DTH22 temperature and humidity sensor using a Raspberry Pi through [MQTT](https://mqtt.org/)

- Utilizes the [`adafruit-circuitpython-dht`](https://github.com/adafruit/Adafruit_CircuitPython_DHT?tab=readme-ov-file) python package
- Integrates seamessly with Home Assistant through MQTT

> **Credit:** Inspired by and adapted from [tofuSCHNITZEL's rpi-screenbrightness-mqtt](https://github.com/tofuSCHNITZEL/rpi-screenbrightness-mqtt/blob/master/rpi_screenbrightness_mqtt/run.py). Many thanks for the great foundation!

## Features

- Publishes the current temperature and humidity
- Automatic Home Assistant MQTT Discovery support
  - Automatically configures itself as a valid device and adds itself as a temperature and humidity entities
- Designed to run on Raspberry Pi

<p align="center">
  <img src="https://github.com/user-attachments/assets/51dba611-1bb3-4545-951d-609ac66dc059" style="height:400px"/>
  <img src="https://github.com/user-attachments/assets/d5cce315-9bed-4bb8-b321-89d36aa65c20" style="height:400px"/>
</p>

## Configuration

Using the given `settings.conf.example` file, create a `settings.conf` file in the root of the project directory

- Fill out its information according to the comments
- More information regarding the `device` field can be found [here](https://www.home-assistant.io/integrations/mqtt/#discovery-examples-with-component-discovery)

Or as an example:

```ini
device = {"name": "Raspberry Pi 4", "identifiers": "pi", "manufacturer": "Raspberry Pi Foundation", "model": "4B"}
```

## Building/Running

Run the provided docker build script `./build.sh` to build the docker image

Here are examples of running the container through docker:

### Docker CLI

```bash
docker run -d \
    --privileged \
    -v /dev/gpiomem:/dev/gpiomem \
    -v /PATH/TO/REPO/settings.conf:/app/settings.conf \
    dht22-mqtt
```

### Docker Compose

```yaml
dht22:
  image: dht22-mqtt
  volumes:
    - /dev/gpiomem:/dev/gpiomem # access the GPIO
    - /PATH/TO/REPO/settings.conf:/app/settings.conf
  privileged: true # needed to access the GPIO
```

> [!NOTE]
> The container might need the `privileged` flag in order to properly access the device's GPIO pins. There might be a better way to do this without giving root access, but I found this to be the easiest method
