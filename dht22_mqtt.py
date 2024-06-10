import board
import os
import time
import sys
import adafruit_dht
#import Adafruit_DHT as dht
import paho.mqtt.client as mqtt
import json

# Settings
INTERVAL=60
next_reading = time.time()

# DHT-11 sensor configuration
#sensor = Adafruit_DHT.DHT11
#pin = 4  # GPIO pin where your sensor is connected
#dhtDevice = adafruit_dht.DHT22(board.D4, use_pulseio=False)
dhtDevice = adafruit_dht.DHT22(board.D18)

# MQTT configuration
mqtt_broker = "192.168.88.14"
mqtt_port = 1883
mqtt_topic = "sensors/temperature_humidity"

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with code " + str(rc))

client = mqtt.Client()
client.username_pw_set(username="mqtt", password="P4ssw0rd")
client.on_connect = on_connect

client.connect(mqtt_broker, mqtt_port, 60)

# while True:
#     temperature = dhtDevice.temperature
#     humidity = dhtDevice.humidity
#     #humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
#     if humidity is not None and temperature is not None:
#         payload = f"{{'temperature': {temperature}, 'humidity': {humidity}}}"
#         client.publish(mqtt_topic, payload)
#     else:
#         print("Failed to read data from the sensor")

# client.loop_forever()
client.loop_start()

try:
    while True:
        try:
            temperature = dhtDevice.temperature
            humidity = dhtDevice.humidity
            if humidity is not None and temperature is not None:
                #payload = f"{{'temperature': {temperature}, 'humidity': {humidity}}}"
                payload = f"{{\"temperature\":\"{temperature}\",\"humidity\":\"{humidity}\"}}"
                client.publish(mqtt_topic, payload)
            else:
                print("Failed to read data from the sensor")

            next_reading += INTERVAL
            sleep_time = next_reading-time.time()
            if sleep_time > 0:
                time.sleep(sleep_time)

        except RuntimeError as error:
            # Errors happen fairly often, DHT's are hard to read, just keep going
            print(error.args[0])
            time.sleep(2.0)
            continue
        except Exception as error:
            dhtDevice.exit()
            raise error

        time.sleep(2.0)
except KeyboardInterrupt:
    pass

client.loop_stop()
client.disconnect()
