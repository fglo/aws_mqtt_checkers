import sys
import uuid
import threading
import time

from Board import *

game_id = str(uuid.uuid4())
if len(sys.argv) > 1:
    game_id = sys.argv[1]

host = False
if len(sys.argv) > 2 and sys.argv[2] == 'host':
    host = True

board = Board(game_id, host = host)