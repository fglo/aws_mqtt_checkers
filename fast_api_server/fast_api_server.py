import paho.mqtt.client as mqtt
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import random
import json
import os
import ssl
import uuid

def clean_board():
    return [
    [0, 2, 0, 2, 0, 2, 0, 2],
    [2, 0, 2, 0, 2, 0, 2, 0],
    [0, 2, 0, 2, 0, 2, 0, 2],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [1, 0, 1, 0, 1, 0, 1, 0],
    [0, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 0]
]

class Game:
    def __init__(self, game_id, host_device_id):
        self.game_id = game_id
        self.host_device_id = host_device_id
        self.secondary_device_id = ""
        self.last_move = None
        self.board = clean_board()

games = {}

topic_prefix = "checkers"
topic_moves = f'{topic_prefix}/%s/moves'
topic_game = f'{topic_prefix}/%s/game'
topic_board = f'{topic_prefix}/%s/board'

mqtt_host = os.environ['MQTT_HOST']
mqtt_port = int(os.environ['MQTT_PORT'])

if os.environ['MQTT_WHERE'] == "aws":
    ca = "./rootCA.crt"
    cert = "./cert.pem"
    private = "./private.key.txt"

class Move(BaseModel):
    device_id: str
    player: int
    from_x: int 
    from_y: int 
    to_x: int 
    to_y: int
    captured_x: int
    captured_y: int

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

client = mqtt.Client(client_id="fast_api_server")
client.on_connect = on_connect

if os.environ['MQTT_WHERE'] == "aws":
    client.tls_set(ca,
        certfile=cert,
        keyfile=private,
        cert_reqs=ssl.CERT_REQUIRED,
        tls_version=ssl.PROTOCOL_TLSv1_2,
        ciphers=None,
    )

client.connect(mqtt_host, mqtt_port, 60)

client.loop_start()

app = FastAPI()

@app.get("/move/{game_id}")
async def get_last_move(game_id : str):
    global games
    return games[game_id].last_move

@app.post("/move/{game_id}") 
async def commit_move(game_id : str, move: Move):
    global games
    print(move)
    
    client.publish(topic_board % game_id, payload=json.dumps({
        'host_device_id': games[game_id].host_device_id,
        'board': games[game_id].board,
        'move_to_x': move.to_y,
        'move_to_y': move.from_y,
    }).encode('utf-8'), qos=1)

    tmp = games[game_id].board[move.to_y][move.to_x]
    games[game_id].board[move.to_y][move.to_x] = games[game_id].board[move.from_y][move.from_x]
    games[game_id].board[move.from_y][move.from_x] = tmp

    move.captured_x = -1
    move.captured_y = -1

    if move.to_x - move.from_x == 2 and move.to_y - move.from_y == 2:
        move.captured_x = move.to_x - 1
        move.captured_y = move.to_y - 1
    elif move.to_x - move.from_x == -2 and move.to_y - move.from_y == 2:
        move.captured_x = move.to_x + 1
        move.captured_y = move.to_y - 1
    elif move.to_x - move.from_x == 2 and move.to_y - move.from_y == -2:
        move.captured_x = move.to_x - 1
        move.captured_y = move.to_y + 1
    elif move.to_x - move.from_x == -2 and move.to_y - move.from_y == -2:
        move.captured_x = move.to_x + 1
        move.captured_y = move.to_y + 1

    if move.captured_x != -1 and move.captured_y != -1:
        games[game_id].board[move.captured_y][move.captured_x] = 0

    games[game_id].last_move = move
    payload=json.dumps({
        "id": str(uuid.uuid4()),
        "device_id": games[game_id].host_device_id,
        "from_x": move.from_x,
        "from_y": move.from_y,
        "to_x": move.to_x,
        "to_y": move.to_y,
        "captured_x": move.captured_x,
        "captured_y": move.captured_y,
    })
    client.publish(topic_moves % game_id, payload=payload.encode('utf-8'), qos=1)

@app.get("/start/{game_id}/{host_device_id}") 
async def start_game(game_id : str, host_device_id : str):
    global games
    games[game_id] = Game(game_id, host_device_id)
    client.publish(topic_game % game_id, payload=f'start'.encode('utf-8'), qos=1)

@app.get("/join/{game_id}/{secondary_device_id}") 
async def join_game(game_id : str, secondary_device_id : str):
    global games
    games[game_id].secondary_device_id = secondary_device_id
    client.publish(topic_game % game_id, payload=f'joined'.encode('utf-8'), qos=1)

