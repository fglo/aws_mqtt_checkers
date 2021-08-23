from sense_emu import SenseHat
# from sense_hat import SenseHat
import paho.mqtt.client as mqtt

import requests
import time
import json
import uuid
import ssl

from Utils import *
from Field import *

class Board:

  def __init__(self, game_id, host):
    self.game_id = game_id
    self.device_id = str(uuid.uuid4())
    self.host = host

    print(self.game_id, self.device_id, self.host)

    if self.host:
      self.player = 0
    else:
      self.player = 1

    topic_prefix = "checkers"
    self.topic_moves = f'{topic_prefix}/{self.game_id}/moves'
    self.topic_game = f'{topic_prefix}/{self.game_id}/game'

    self.senseHat = SenseHat()
    self.senseHat.low_light = False
    self.senseHat.set_pixels(initial_boards[self.player]())

    self.fast_api_url = 'http://192.168.1.22:8000'
    self.url_moves = f'{self.fast_api_url}/move/'
    self.url_start_game = f'{self.fast_api_url}/start/'
    self.url_join_game = f'{self.fast_api_url}/join/'
    
    mqtt_host = '192.168.1.22'
    mqtt_port = 1883

    ca = "../certs/rootCA.crt"
    cert = "../certs/user11.cert.pem"
    private = "../certs/user11.private.key.txt"
    
    self.client = mqtt.Client(client_id=f"board-{self.device_id}")

    self.client.on_connect = self.on_connect
    self.client.on_message = self.on_message

    self.client.tls_set(ca,
        certfile=cert,
        keyfile=private,
        cert_reqs=ssl.CERT_REQUIRED,
        tls_version=ssl.PROTOCOL_TLSv1_2,
        ciphers=None,
    )

    self.client.connect(mqtt_host, mqtt_port, 60)

    self.game_started = False

    self.client.loop_forever()

  def start_game(self):
    print("starting game...")

    self.game_started = True

    response = requests.get(self.url_start_game + self.game_id + "/" + self.device_id)

    self.color = white
    self.opponent_color = blue

  def join_game(self):
    print("joining game...")

    response = requests.get(self.url_join_game + self.game_id + "/" + self.device_id)

    self.color = blue
    self.opponent_color = white

  def wait_for_move(self):
    print("waiting for move...")
    showed_moves = False
    move_confirmed = False

    curr_position = Field(self.senseHat, starting_positions[self.player][0], starting_positions[self.player][1])
    curr_position.setColor(yellow)

    while not move_confirmed:
      event = self.senseHat.stick.wait_for_event()

      if event.action is "pressed":
        print(event.direction)

        if event.direction is not "middle":
          curr_position.handle_joystick_move(event.direction)
          
        else:
          if not showed_moves:
            move_from = [curr_position.x, curr_position.y]

            if curr_position.isPawn():
              selected_pawn = curr_position.copy()
              selected_pawn.getPotentialMoves()

              if len(selected_pawn.moves) > 0:
                showed_moves = True

          else:
            move_to = [curr_position.x, curr_position.y]

            for move in selected_pawn.moves:
              if move.curr_color == green:   
                move.setColor(nothing)

            if selected_pawn is not None and curr_position.prev_color == green:

              curr_position.setPawn(selected_pawn.prev_color)

              for move in selected_pawn.moves:
                if move.x == curr_position.x and move.y == curr_position.y:   
                  print(move.captures is not None)
                  if move.captures is not None:
                    move.captures.turnOf()
                    print(getColorName(move.captures.prev_color) + " pawn was captured")
                  break
              
              selected_pawn.setColor(nothing)
              move_confirmed = True
              self.confirm_move(move_from, move_to)

            selected_pawn = None
            showed_moves = False

  def confirm_move(self, move_from, move_to):
    payload = f'{move_from[0]};{move_from[1]};{move_to[0]};{move_to[1]}'

    if self.player == 1:
      move_from_x = 7 - move_from[0]
      move_from_y = 7 - move_from[1]
      move_to_x = 7 - move_to[0]
      move_to_y = 7 - move_to[1]
    else:
      move_from_x = move_from[0]
      move_from_y = move_from[1]
      move_to_x = move_to[0]
      move_to_y = move_to[1]

    move = {
        "device_id": self.device_id,
        "player": self.player,
        "from_x": move_from_x, 
        "from_y": move_from_y, 
        "to_x": move_to_x,
        "to_y": move_to_y,
        "captured_x": -1,
        "captured_y": -1
      }

    response = requests.post(self.url_moves + self.game_id, json=move)
    print(response.text)

  def handle_player_move(self, move):
    if self.player == 1:
      move_from_x = 7 - move['from_x']
      move_from_y = 7 - move['from_y']
      move_to_x = 7 - move['to_x']
      move_to_y = 7 - move['to_y']

      if move['captured_x'] != -1 and move['captured_y'] != -1:
        captured = Field(self.senseHat, 7 - move['captured_x'], 7 - move['captured_y'])
        captured.turnOf()
    else:
      move_from_x = move['from_x']
      move_from_y = move['from_y']
      move_to_x = move['to_x']
      move_to_y = move['to_y']

      if move['captured_x'] != -1 and move['captured_y'] != -1:
        captured = Field(self.senseHat, move['captured_x'], move['captured_y'])
        captured.turnOf()

    color1 = self.senseHat.get_pixel(move_from_x, move_from_y)
    color2 = self.senseHat.get_pixel(move_to_x, move_to_y)
    self.senseHat.set_pixel(move_from_x, move_from_y, color2)
    self.senseHat.set_pixel(move_to_x, move_to_y, color1)

    self.wait_for_move()

  def on_connect(self, client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    
    self.client.subscribe(self.topic_moves, qos=1)
    self.client.subscribe(self.topic_game, qos=1)
    
    if self.host and not self.game_started:
      self.start_game()
      
  def on_message(self, client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    print(f'{msg.topic} {payload}', flush=True)

    if msg.topic == self.topic_game:
      if payload == 'start' and not self.game_started:
        self.join_game()
      if payload == 'joined' and self.game_started:
        self.wait_for_move()
    elif msg.topic == self.topic_moves:
      response = requests.get(self.url_moves + self.game_id)
      move = json.loads(response.text)
      print(move)

      if move['device_id'] != self.device_id:
        self.handle_player_move(move)

