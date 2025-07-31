import configparser
import json
import sys
import time

import adafruit_dht
import board
import paho.mqtt.client as mqtt


class MQTTControl:

    def __init__(self, config_path) -> None:
        self._config = configparser.ConfigParser()
        if len(self._config.read(config_path)) == 0:
            raise RuntimeError(
                "Failed to find configuration file at {0}, is the application properly installed?".format(
                    config_path
                )
            )

        self._mqtt_broker = self._config.get("mqtt", "broker")
        self._mqtt_user = self._config.get("mqtt", "user")
        self._mqtt_password = self._config.get("mqtt", "password")
        self._mqtt_connected = False
        self._mqtt_clientid = self._config.get("mqtt", "clientid")

        self._mqtt_temp_topic = self._config.get("mqtt", "temp_topic")
        self._mqtt_hum_topic = self._config.get("mqtt", "hum_topic")
        self._mqtt_device = json.loads(self._config.get("mqtt", "device"))

        self._mqtt_discovery_prefix = self._config.get("mqtt", "discovery_prefix")

        # Detect the sensor
        try:
            self.sensor = adafruit_dht.DHT22(board.D24)
        except Exception as e:
            raise RuntimeError("ABORT: Could not detect the DHT22 sensor on pin 24.")

    def on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            print("Connected!")
            self._mqtt_connected = True

            # Listen for when Home Assistant goes online
            client.subscribe(f"{self._mqtt_discovery_prefix}/status")
            self.send_discovery(client)
        else:
            self._mqtt_connected = False
            print("Could not connect. Return code: " + str(reason_code))

    def on_disconnect(self, client, userdata, flags, reason_code, properties):
        print("Disconnected. Reason: " + str(reason_code))
        self._mqtt_connected = False

    def send_status(self, client):
        payload_temp = str(self.sensor.temperature)
        payload_humidity = str(self.sensor.humidity)

        print(f"Publishing temp: {payload_temp}, hum: {payload_humidity}")
        client.publish(self._mqtt_temp_topic, payload_temp, 0, False)
        client.publish(self._mqtt_hum_topic, payload_humidity, 0, False)

    def on_message(self, client, userdata, msg):
        payload = str(msg.payload.decode("utf-8"))
        topic = msg.topic

        if topic == f"{self._mqtt_discovery_prefix}/status":
            # Send discovery message when homeassistant is online
            if str(payload) == "online":
                self.send_discovery(client)

    def send_discovery(self, client):
        """Sends a discovery message whenever home assistant is detected to be online"""
        tempDiscovery = (
            f"{self._mqtt_discovery_prefix}/sensor/{self._mqtt_clientid}-temp/config"
        )
        humDiscovery = (
            f"{self._mqtt_discovery_prefix}/sensor/{self._mqtt_clientid}-hum/config"
        )

        tempConfig = {
            "name": self._mqtt_clientid + "-temp",
            "unique_id": self._mqtt_clientid + "-temp",
            "state_topic": self._mqtt_temp_topic,
            "unit_of_measurement": "°C",
            "device_class": "temperature",
            "device": self._mqtt_device,
        }

        humConfig = {
            "name": self._mqtt_clientid + "-hum",
            "unique_id": self._mqtt_clientid + "-hum",
            "state_topic": self._mqtt_hum_topic,
            "unit_of_measurement": "%",
            "device_class": "humidity",
            "device": self._mqtt_device,
        }

        print("Sending temp discovery message...")
        client.publish(tempDiscovery, json.dumps(tempConfig), 0, False)
        print("Sending humidity discovery message...")
        client.publish(humDiscovery, json.dumps(humConfig), 0, False)
        self.send_status(client)

    def run(self):
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, self._mqtt_clientid)
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.on_disconnect = self.on_disconnect
        client.username_pw_set(self._mqtt_user, self._mqtt_password)

        print("Connecting to broker " + self._mqtt_broker)
        client.loop_start()
        try:
            client.connect(self._mqtt_broker, 1883, 60)
        except:
            print("ABORT: Connection failed!")
            exit(1)

        while not self._mqtt_connected:
            time.sleep(1)
        while self._mqtt_connected:
            try:
                self.send_status(client)
            except Exception as e:
                print("exception")
                print(str(e))

            time.sleep(10)

        client.loop_stop()  # Stop loop
        client.disconnect()  # disconnect


if __name__ == "__main__":
    print("Starting rpi DHT22 sensor control via mqtt")

    config_path = "./settings.conf"
    # Override config path if provided as parameter.
    if len(sys.argv) == 2:
        config_path = sys.argv[1]

    controller = MQTTControl(config_path)
    controller.run()
