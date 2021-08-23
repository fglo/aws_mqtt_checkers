green = [0, 252, 0]
yellow = [255, 255, 0]
blue = [0, 0, 248]
red = [248, 0, 0]
white = [248, 252, 248]
gray = [100, 100, 100]
nothing = [0, 0, 0]
pink = [255, 105, 180]

starting_positions = [(3, 7), (3, 7)]

def getColorName(color):
  if color == white:
    return "white"
  if color == blue:
    return "blue"

def initial_checkers_board():
    B = blue
    O = nothing
    W = white
    board = [
    O, B, O, B, O, B, O, B,
    B, O, B, O, B, O, B, O,
    O, B, O, B, O, B, O, B,
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    W, O, W, O, W, O, W, O,
    O, W, O, W, O, W, O, W,
    W, O, W, O, W, O, W, O,
    ]
    return board

def initial_checkers_board2():
    B = blue
    O = nothing
    W = white
    board = [
    O, W, O, W, O, W, O, W,
    W, O, W, O, W, O, W, O,
    O, W, O, W, O, W, O, W,
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    B, O, B, O, B, O, B, O,
    O, B, O, B, O, B, O, B,
    B, O, B, O, B, O, B, O,
    ]
    return board
    
initial_boards = [initial_checkers_board, initial_checkers_board2]
