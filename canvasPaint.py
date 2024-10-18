# importing libraries
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import heapq
from PIL import Image
import operator

# THIS SHOULD HANDLE UPDATING CANVAS
class paintWindow(QLabel):
  def __init__(self):
    super().__init__()
    # screen size with changes for canvas
    self.maxX = 1000
    self.maxY = 800
    self.maxSize = (self.maxX, self.maxY)
    self.dX = 100
    self.dY = 100

    #create our pixmap instead of image
    self.pixMap = QPixmap(self.maxX-self.dX, self.maxY-self.dY)
    self.pixMap.fill(Qt.white)
    self.setPixmap(self.pixMap)

    self.brushColour = QColor('#000000') #BLACK

    self.brushSize = 4
    self.lastPoint = QPoint()

    # Change our Cursor Image 
    cursorImage = QPixmap('cursorPencil.png')
    cursor = QCursor(cursorImage, 0, cursorImage.height())
    self.setCursor(cursor)

    #connect Point settings
    self.connectColour = Qt.black
    self.traversableColour = Qt.white

  #--------------------------Brush Actions------------------------------
  def changeBrushColour(self, colour):
    self.brushColour = QColor(colour)

  def changeBrushSize(self, size):
    self.brushSize = size
  #------------------------- -Brush Actions------------------------------
  
  def save(self):
    filePath, _ = QFileDialog.getSaveFileName(self, "Save Image", "",
                      "PNG(*.png);;JPEG(*.jpg *.jpeg);;All Files(*.*) ")

    if filePath == "":
      return
    image = self.pixMap.toImage()
    image.save(filePath)
  
  def clear(self):
    self.pixMap.fill(Qt.white)
    self.setPixmap(self.pixMap)

  def open(self):
    name, _ = QFileDialog.getOpenFileName(
                                          self, 
                                          'Open File', #name of window 
                                          "", #search 
                                          "PNG(*.png);;JPEG(*.jpg *.jpeg)" #accepted file types
                                          ) 
    if name:
      self.clear()
      print('Opening Image')
      openImage = Image.open(name)
      w, h = openImage.size
      if (w*h)>((self.maxX-100)*(self.maxY-self.dY)):
        openImage.thumbnail(self.maxSize)
        w,h = openImage.size
      self.masterList = {}
      self.createMasterList(openImage, w,h, switch=1)
      self.autoPaint(switch=1)

  #-------------------------Mouse Movements-----------------------------
  def mousePressEvent(self, event):
    if event.button() == Qt.LeftButton:
      self.drawing = True
      # make last point to the point of cursor
      self.lastPoint = event.pos()
      self.draw(
        draw=event, 
        position=self.lastPoint
      )

  def mouseMoveEvent(self, event):
    if (event.buttons() & Qt.LeftButton) & self.drawing:
      self.draw(
        draw=event, 
        position=self.lastPoint
      )

  def mouseReleaseEvent(self, event):
    if event.button() == Qt.LeftButton:
      # make drawing flag false
      self.drawing = False
  #-------------------------Mouse Movements-----------------------------
  def draw(self, draw, position):
    #change our paints in reference to our template
    # nextpoint = QPoint(draw.pos().x(), int(draw.pos().y()-self.dY/2))
    # currpoint = QPoint(position.x(), int(position.y()-self.dY/2))
    nextpoint = QPoint(draw.pos().x(), int(draw.pos().y()))
    currpoint = QPoint(position.x(), int(position.y()))

    # Set our painter and change our pen
    painter = QPainter(self.pixmap())
    # painter = QPainter(self.pixMap)
    painter.setPen(QPen(self.brushColour, self.brushSize, 
                    Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    #DRAW POINTS
    # this means we click no drag
    if nextpoint == currpoint:
      painter.drawPoint(currpoint)
    painter.drawLine(currpoint, nextpoint)
    painter.end()
    self.update()
    self.pixMap = QPixmap(self.pixmap())
    self.lastPoint = draw.pos()

  #ANIMATION WORKS WOHOOO NOW WE MUST MAKE THIS BETTER
  def animate(self):
    self.timer.start(10)
  
  def autoPaint(self, switch):
    # create a timer object for our window
    self.timer = QTimer(self)
    if switch == 1:
      self.timer.timeout.connect(self.paintImage)
    # if switch == 2:
      # self.timer.
    self.animate()
  
  def createMasterList(self, image, w, h, switch):
    for x in range(w):
      for y in range(h):
        # list for PIL images, creating dict {colour: [points]}
        if switch == 1:
          colourVal = image.getpixel((x,y))
          if colourVal not in self.masterList:
            self.masterList[colourVal]=[(x,y)]
          else:
            self.masterList[colourVal].append((x,y))
        
        # for connecting points 
        if switch == 2:
          colour = QColor(image.pixel(x,y))
          if (x,y) not in self.masterList:
            self.masterList[x,y] = colour
          if colour == Qt.black:
            self.startPointList.append((x,y))

  def paintImage(self):
    if len(self.masterList)>0:
      # get painter, list of keys and start looping throuhg colours 
      painter = QPainter(self.pixmap())
      colourKeys = list(self.masterList.keys())
      for colour in colourKeys:
        # get list of points for said colour, paint 10 items in list (gets X)
        cordList = self.masterList[colour]
        for i in range(10):
          if not cordList:
            del self.masterList[colour]
            break
          #pop point, drawpoint and incement to next point
          cord = cordList.pop(0)
          paintColour = QColor(*colour)
          painter.setPen(paintColour)
          painter.drawPoint(*cord)
          i+=1
      # End the painting and update the label/pixmap
      painter.end()
      self.update()
      self.pixMap = QPixmap(self.pixmap())
    else:
      print('--Finished--')
      self.timer.stop()
  
  def connect(self):
    #intialize lists and variables to create our master Lists
    self.masterList = {}
    self.startPointList = []
    image = self.pixMap.toImage()
    w = image.width()
    h = image.height()
    self.createMasterList(image, w, h, switch=2)

    # # Loop through points we want to connect 
    # i = 0
    # while i < len(self.listColoursPoints):
    #   if (i+1) == len(self.listColoursPoints):
    #     break
    #   # print(self.listColoursPoints[i],self.listColoursPoints[i+1])
    #   self.getPath(self.listColoursPoints[i],self.listColoursPoints[i+1])
    #   i+=1
    # size = len(self.listColoursPoints)


    # if size <=0:
    #   print('No Points Found')
    # elif size==1:
    #   print('One point found')
    # else: 
    #   # paint our paths
    #   print('Connecting Points')
    #   self.automatePaint()
