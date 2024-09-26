# importing libraries
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
import time
import numpy as np
from scipy.spatial import cKDTree
from scipy.spatial.distance import cdist

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

  def createLists(self):
    if len(self.copyofLCP) > 1:
      refPoint = self.copyofLCP.pop(0)
      copyList = np.array(self.copyofLCP )
      distances = cdist([refPoint], copyList)[0]
      # Find the index of the closest point
      closest_index = np.argmin(distances)
      # print(closest_index)
      closest_point = copyList[closest_index]
      self.listNxtPoints.append(closest_point)
      # print(closest_point)
      self.createLists()
    else:
      return  

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
    for y in range(self.image.height()):
      for x in range(self.image.width()):
        colour = QColor(self.image.pixel(x,y))
        if colour !=Qt.white:
          # self.listColoursPoints.append(QPoint(x,y))
          self.listColoursPoints.append((x,y))
    
    self.listNxtPoints = []
    self.copyofLCP = self.listColoursPoints.copy()
    self.createLists()
    self.listNxtPoints = [(tuple(point)) for point in self.listNxtPoints]
 
    self.timer = QTimer(self)
    self.timer.timeout.connect(self.colourPoints)
    self.timer.start(100)  # Start the timer, it will call draw_lines() every 100 ms
   
    # TODO: Get list of points, and use algorithm to connect them together
      # TODO: Change list so that it contains the point and the closet point next to it
      # TODO: We get multiple points for each colour work on this 
      # TODO: 
    # TODO: depending on brush size change how the algorithm works 
    # TODO:  
# create pyqt5 app
App = QApplication(sys.argv)
 
# create the instance of our Window
window = Window()
 
# showing the window
window.show()
 
# start the app
sys.exit(App.exec())