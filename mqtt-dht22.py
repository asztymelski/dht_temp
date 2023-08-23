import board
import os
import time
import sys
import adafruit_dht
#import Adafruit_DHT as dht
import paho.mqtt.client as mqtt
import json

THINGSBOARD_HOST = 'demo.thingsboard.io'
ACCESS_TOKEN = 'DHT22_DEMO_TOKEN'
dhtDevice = adafruit_dht.DHT22(board.D6)

# Data capture and upload interval in seconds. Less interval will eventually hang the DHT22.
INTERVAL=1

sensor_data = {'temperature': 0, 'humidity': 0}

next_reading = time.time() 

client = mqtt.Client()

# Set access token
client.username_pw_set(username="mqtt", password="P4ssw0rd")
# Connect to ThingsBoard using default MQTT port and 60 seconds keepalive interval
client.connect("mosquitto.sycowa", 1883, 60)

client.loop_start()

try:
    while True:
        try:
            #humidity,temperature = dht.read_retry(dht.DHT22, 6)
            temperature = dhtDevice.temperature
            humidity = dhtDevice.humidity
            humidity = round(humidity, 2)
            temperature = round(temperature, 2)
            #print(u"Temperature: {:g}\u00b0C, Humidity: {:g}%".format(temperature, humidity))
        
            sensor_data['temperature'] = temperature
            sensor_data['humidity'] = humidity

            # Sending humidity and temperature data to HA
            client.publish('/pizero/dht22', json.dumps(sensor_data), 1)

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
