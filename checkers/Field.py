from Utils import *

class Field:

  def __init__(self, board, x, y):
    self.board = board
    self.x = x % 8
    self.y = y % 8
    self.prev_color = self.board.get_pixel(self.x, self.y)
    self.curr_color = self.board.get_pixel(self.x, self.y)
    self.moves = []
    self.captures = None

  def changeX(self, change):
    x = self.x + change
    if x >= 0 and x <= 7:
      self.x = x
      self.__updateColor__()

  def changeY(self, change):
    y = self.y + change
    if y >= 0 and y <= 7:
      self.y = y
      self.__updateColor__()

  def changeCoords(self, changeX, changeY):
    x = self.x + changeX
    y = self.y + changeY
    if x >= 0 and x <= 7 and y >= 0 and y <= 7:
      self.x = x
      self.y = y
      self.__updateColor__()

  def checkMove(self, shiftX, shiftY):
    x = self.x + shiftX
    y = self.y + shiftY

    m = None
    if x >= 0 and x <= 7 and y >= 0 and y <= 7:
      m = Field(self.board, x, y)

    if m is not None:
      if m.curr_color == nothing:
        m.setColor(green)
        self.moves.append(m)
      elif m.isOppositePawn(self.prev_color):
        m.changeCoords(shiftX, shiftY)
        if m.curr_color == nothing:
          m.setColor(green)
          m.captures = Field(self.board, self.x + shiftX, self.y + shiftY)
          self.moves.append(m)


  def getPotentialMoves(self):
    self.moves = []

    self.checkMove(-1, -1)
    self.checkMove(-1, 1)
    self.checkMove(1, -1)
    self.checkMove(1, 1)

    return self.moves

  def isPawn(self):
    print(self.prev_color, white, blue)
    return self.prev_color == white or self.prev_color == blue

  def isOppositePawn(self, color):
    return self.prev_color != color and (self.prev_color == white or self.prev_color == blue) 

  def setColor(self, color):
    self.prev_color = self.curr_color
    self.curr_color = color
    self.__updateBoard__()
    
  def setPawn(self, color):
    self.prev_color = color
    self.curr_color = color
    self.__updateBoard__()

  def turnOf(self):
    self.setColor(nothing)
    self.__updateBoard__()

  def setColorAsPrevColor(self):
    self.curr_color = self.prev_color
    self.__updateBoard__()

  def __updateBoard__(self):
    self.board.set_pixel(self.x, self.y, self.curr_color)

  def __updateColor__(self):
    self.prev_color = self.curr_color
    self.curr_color = self.board.get_pixel(self.x, self.y)

  def handle_joystick_move(self, direction):
    self.setColorAsPrevColor()

    print(self.prev_color)

    if direction is "up":
      self.changeY(-1)
    if direction is "down":
      self.changeY(1)
    if direction is "left":
      self.changeX(-1)
    if direction is "right":
      self.changeX(1)

    self.__updateColor__()

    if self.isPawn():
      self.setColor(red)
    else:
      self.setColor(yellow)

  def copy(self):
    copy = Field(self.board, self.x, self.y)
    copy.prev_color = self.prev_color
    return copy