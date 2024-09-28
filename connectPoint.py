# importing libraries
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
import time
import numpy as np
from scipy.spatial import cKDTree
from scipy.spatial.distance import cdist
import heapq


# window class
class Window(QMainWindow):
  def __init__(self):
    super().__init__()
    # setting title
    self.setWindowTitle("Paint with PyQt5")

    # setting geometry to main window
    self.setGeometry(100, 100, 800, 600)
    # self.setGeometry(100, 100, 100, 100)


    # creating image object
    self.image = QImage(self.size(), QImage.Format_RGB32)
    self.image.fill(Qt.white)

    # drawing flag
    self.drawing = False
    # default brush size abd colour
    self.brushSize = 1
    self.brushColor = Qt.black

    # QPoint object to tract the point
    self.lastPoint = QPoint()

    # creating menu bar
    mainMenu = self.menuBar()
    # addiding menues to the main menu
    self.fileMenu = mainMenu.addMenu("File")
    self.brushMenu = mainMenu.addMenu("Brush Size")
    self.colourMenu = mainMenu.addMenu("Brush Color")

    self.addSizeButtons()
    self.addColourButtons()
    self.addFileButtons()

  #-----------------------------------ADD BUTTONS-----------------------
  # add buttons to size menue
  def addSizeButtons(self):
    #-----------creating options for brush sizes-----------------------
    # creating action for selecting pixel of 4px, adding this action to 
    # the brush menu, then we connect a button 
    px4 = QAction("4px", self) #button 
    self.brushMenu.addAction(px4) #button -> menu
    px4.triggered.connect(lambda: self.setBrushSize(4)) # add action to button

    # similarly repeating above steps for different sizes
    px7 = QAction("7px", self)
    self.brushMenu.addAction(px7)
    px7.triggered.connect(lambda: self.setBrushSize(7))

    px9 = QAction("9px", self)
    self.brushMenu.addAction(px9)
    px9.triggered.connect(lambda: self.setBrushSize(9))

    px12 = QAction("12px", self)
    self.brushMenu.addAction(px12)
    px12.triggered.connect(lambda: self.setBrushSize(12))
    #-----------creating options for brush sizes-----------------------
  
  # add buttons to colour menu
  def addColourButtons(self):
    # black button added to menu and adding action to menu
    black = QAction("Black", self)
    self.colourMenu.addAction(black)
    black.triggered.connect(lambda: self.changeColour('black'))

    white = QAction("White", self)
    self.colourMenu.addAction(white)
    white.triggered.connect(lambda: self.changeColour('white'))

    green = QAction("Green", self)
    self.colourMenu.addAction(green)
    green.triggered.connect(lambda: self.changeColour('green'))
    
    yellow = QAction("Yellow", self)
    self.colourMenu.addAction(yellow)
    yellow.triggered.connect(lambda: self.changeColour('yellow'))

    red = QAction("Red", self)
    self.colourMenu.addAction(red)
    red.triggered.connect(lambda: self.changeColour('red'))
 
  # add buttons to file menu
  def addFileButtons(self):
    # creating save action
    saveAction = QAction("Save", self)
    saveAction.setShortcut("Ctrl + S") # adding short cut for save action
    self.fileMenu.addAction(saveAction)
    saveAction.triggered.connect(self.save)

    # creating clear action
    clearAction = QAction("Clear", self)
    self.fileMenu.addAction(clearAction)
    clearAction.triggered.connect(self.clear)

    #draw points button 
    connectPointButton = QAction('Connect Points', self)
    self.fileMenu.addAction(connectPointButton)
    connectPointButton.triggered.connect(self.connectPoints)
  #-----------------------------------ADD BUTTONS-----------------------


  #----------------------------------MOUSE EVENTS-----------------------
  # method for checking mouse cicks
  def mousePressEvent(self, event):
    # if left mouse button is pressed
    if event.button() == Qt.LeftButton:
      # make drawing flag true
      self.drawing = True
      # make last point to the point of cursor
      self.lastPoint = event.pos()
      self.mouseDraw(
        draw=event, 
        position=self.lastPoint
      )
      
  # METHOD FOR WHEN MOUSE MOVES
  def mouseMoveEvent(self, event):
    # checking if left button is pressed and drawing flag is true
    if (event.buttons() & Qt.LeftButton) & self.drawing:
      self.mouseDraw(
        draw=event,
        position=self.lastPoint,
        drag=True
      )

  # method for mouse left button release
  def mouseReleaseEvent(self, event):

    if event.button() == Qt.LeftButton:
        # make drawing flag false
        self.drawing = False

  # draw on application
  def mouseDraw(self, draw, position, drag=False):
    # creating painter object
      painter = QPainter(self.image)
        
      # set the pen of the painter
      painter.setPen(QPen(self.brushColor, self.brushSize, 
                      Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

      # if drag is True, the mouse is clicked and moving so we draw from 
      # point to point 
      if drag:
        painter.drawLine(self.lastPoint, draw.pos())
      # else we are just clicking so draw at that point
      else:
        painter.drawPoint(self.lastPoint)
        # creating painter object

      # change the last point and update the the image
      self.lastPoint = draw.pos()  
      self.update()
  
  # paint event
  def paintEvent(self, event):
    # create a canvas
    canvasPainter = QPainter(self)
      
    # draw rectangle  on the canvas
    canvasPainter.drawImage(self.rect(), self.image, self.image.rect())
  #----------------------------------MOUSE EVENTS-----------------------


  # method for saving canvas
  def save(self):
    filePath, _ = QFileDialog.getSaveFileName(self, "Save Image", "",
                      "PNG(*.png);;JPEG(*.jpg *.jpeg);;All Files(*.*) ")

    if filePath == "":
        return
    self.image.save(filePath)

  # method for clearing every thing on canvas
  def clear(self):
    # make the whole canvas white
    self.image.fill(Qt.white)
    # update
    self.update()

  # method for changing brush size (size in pixels)
  def setBrushSize(self, size):
    self.brushSize = size

  # method to change brush colour (uses strings in lowercase)
  def changeColour(self, colour):
    try:
        color_attr = getattr(Qt, colour)
        self.brushColor = color_attr
    except AttributeError:
        # Handle the case where the color name is not found
        self.brushColor = Qt.black

  def heuristic(x1, y1, x2, y2):
    """
    Heuristic function for A* search (Manhattan distance).
    """

    # This can be changed to a less costly method which doesnt do the full 
    # calculation but does an "approximation" or guess using different methods
    # Instead of finding the absolute difference we use a different method 
    # h = sqrt( (current_cell.x – goal.x)2 + 
            # (current_cell.y – goal.y)2 )
    h = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5 # eculedian
    # return abs(x1 - x2) + abs(y1 - y2)  #manhattan calc
    return h
  
  def connectDots(self, start, end):
    # Create a dictionary to store the 2D matrix data
    masterMatrix = {(x, y): color for x, y, color in self.masterList}

    # Define the traversable and wall colors
    # traversableColor = [(255, 255, 255)]  # White color
    traversableColor = QPoint.white  # White color

    # wall_colors = [(0, 0, 0)]  # Black color antyhing not black

    # Initialize the A* search
    queue = [(0, start[0], start[1])] # (fScore, x, y) Lowest fScore will be at front
    cameFrom = {}
    gScore = {(start[0], start[1]): 0} #Dictonary to keep track of points we visted and their gScores
    fScore = {(start[0], start[1]): self.heuristic(*start, *end)} #Same as gScore expect for fScore

    while queue:
      # get the first item in queue
      f, x, y = heapq.heappop(queue)

      # if we hit our end point, we get all the points in the cam from 
      # dict and add those to our path (this will be in reverse order)
      if (x,y) == end:
        self.path = [(x,y)]
        while (x, y) in cameFrom:
          x, y = cameFrom[(x, y)]
          self.path.append((x, y))
        self.path = self.path[::-1]
        return
      
      # check each direction for the current point we are on to see if 
      # which point we should move to next
      for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
        # get the points surronding our current point 
        checkX, checkY = x+dx, y+dy
        # if (checkX, checkY) in masterMatrix and masterMatrix[(checkX,checkY)] in 
      # if len(self.copyofLCP) > 1:
    #   refPoint = self.copyofLCP.pop(0)
    #   copyList = np.array(self.copyofLCP )
    #   distances = cdist([refPoint], copyList)[0]
    #   # Find the index of the closest point
    #   closest_index = np.argmin(distances)
    #   # print(closest_index)
    #   closest_point = copyList[closest_index]
    #   self.listNxtPoints.append(closest_point)
    #   # print(closest_point)
    #   self.createLists()
    # else:
    #   return  

  def colourPoints(self):
    # creating painter object
    if len(self.listNxtPoints) > 0:
      painter = QPainter(self.image)
        
      # set the pen of the painter
      painter.setPen(QPen(self.brushColor, self.brushSize, 
                      Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
      point1 = QPoint(*self.listColoursPoints.pop(0))
      point2 = QPoint(*self.listNxtPoints.pop(0))
      painter.drawLine(point1, point2)
      self.update()
      QTimer.singleShot(100, self.colourPoints)
    else: 
      self.timer.stop()
      return

  def connectPoints(self):
    self.listColoursPoints = []
    self.masterList = []
    # Loop Through each pixel in image and get the colour and point
    for y in range(self.image.height()):
      for x in range(self.image.width()):
        colour = QColor(self.image.pixel(x,y))
        self.masterList.append((x,y,colour))
        if colour == Qt.black:
          self.listColoursPoints.append((x,y))
    # Loop through points we want to connect 
    # print(self.masterList[:-1])
    print(len(self.listColoursPoints))
    i = 0
    while i < len(self.listColoursPoints):
      if (i+1) == len(self.listColoursPoints):
        break
      print(self.listColoursPoints[i],self.listColoursPoints[i+1])
      # self.connectDots(self.listColoursPoints[i],self.listColoursPoints[i+1])
      i+=1


    # THIS WILL BE TO DRAW THE POINTS
    # self.timer = QTimer(self)
    # self.timer.timeout.connect(self.colourPoints)
    # self.timer.start(100)  # Start the timer, it will call draw_lines() every 100 ms
   
  # TODO: send masterList to algorithm to get array of points to draw
      #TODO: Perform algorithm
  # TODO: Draw this new array to connect the points
# create pyqt5 app
App = QApplication(sys.argv)
 
# create the instance of our Window
window = Window()
 
# showing the window
window.show()
 
# start the app
sys.exit(App.exec())