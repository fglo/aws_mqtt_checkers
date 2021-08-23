import paho.mqtt.client as mqtt
import sys
import os
import json
import ssl
from datetime import datetime

topic_prefix = "checkers"
topic_board = f'{topic_prefix}/+/board'

mqtt_host = os.environ['MQTT_HOST']
mqtt_port = int(os.environ['MQTT_PORT'])

if os.environ['MQTT_WHERE'] == "aws":
    ca = "./rootCA.crt"
    cert = "./cert.pem"
    private = "./private.key.txt"

print("mqtt host:", mqtt_host)
print("mqtt port:", mqtt_port)

with open("messages.csv", "w") as file:
    file.write(f'topic;host_device_id;chessboard;move_to_x;move_to_y;datetime\n')

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(topic_board, qos=1)
    
def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    print(f'{msg.topic} {payload}', flush=True)
    
    with open("messages.csv", "a") as file:
        message = json.loads(payload)
        file.write(f'{msg.topic};{message["host_device_id"]};{message["board"]};{message["move_to_x"]};{message["move_to_y"]};{str(datetime.now())[:-3]}\n')
        
client = mqtt.Client(client_id="mqtt_sub")
client.on_connect = on_connect
client.on_message = on_message

if os.environ['MQTT_WHERE'] == "aws":
    client.tls_set(ca,
        certfile=cert,
        keyfile=private,
        cert_reqs=ssl.CERT_REQUIRED,
        tls_version=ssl.PROTOCOL_TLSv1_2,
        ciphers=None,
    )

client.connect(mqtt_host, int(mqtt_port), 60)

client.loop_forever()