# importing libraries
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import heapq
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
    self.black = Qt.black
    self.white = Qt.white

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
      openImage = QImage(name)
      w = openImage.width()
      h = openImage.height()
      if (w*h)>((self.maxX-100)*(self.maxY-self.dY)):
        openImage = openImage.scaled(self.maxX, self.maxY, Qt.AspectRatioMode.KeepAspectRatio)
        w = openImage.width()
        h = openImage.height()
      self.masterList = {}
      self.switch = 1
      self.createMasterList(openImage, w,h)
      self.autoPaint()

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
    nextpoint = QPoint(draw.pos().x(), int(draw.pos().y()))
    currpoint = QPoint(position.x(), int(position.y()))

    # Set our painter and change our pen
    painter = QPainter(self.pixmap())
    painter.setPen(QPen(
                        self.brushColour, 
                        self.brushSize, 
                        Qt.SolidLine, 
                        Qt.RoundCap, 
                        Qt.RoundJoin
                        )
                      )
    
    # this means we click no drag
    if nextpoint == currpoint:
      painter.drawPoint(currpoint)
    # draw and update image
    painter.drawLine(currpoint, nextpoint)
    painter.end()
    self.update()
    self.pixMap = QPixmap(self.pixmap())
    self.lastPoint = draw.pos()

  def paintpoint(self, x, y):
    point1 = QPoint(x, y)
    # Set our painter and change our pen
    painter = QPainter(self.pixmap())
    
    painter.drawPoint(point1)
    painter.end()
    self.update()
    self.pixMap = QPixmap(self.pixmap())

  def animate(self):
    self.timer.start(10)
  
  def autoPaint(self):
    # create a timer object for our window
    self.timer = QTimer(self)
    self.timer.timeout.connect(self.paintImage)
    self.animate()
  
  def createMasterList(self, image, w, h):
    for x in range(w):
      for y in range(h):
        # for opening images
        colour = image.pixel(x,y)
        if self.switch == 1:
          if colour not in self.masterList:
            self.masterList[colour]=[(x,y)]
          else:
            self.masterList[colour].append((x,y))
          
        # for connecting points 
        if self.switch == 2:
          colour = QColor(colour)
          if (x,y) not in self.masterList:
            self.masterList[x,y] = colour
          if colour == self.black:
            self.startPointList.append((x,y))

  def paintImage(self):
    # recursive loop to auto paint masterList -> masterList should be a 
    # dictonary of lists, and these lists contain points.
    if len(self.masterList)>0:
      # get painter, list of keys and start looping through colours 
      painter = QPainter(self.pixmap())
      keys = list(self.masterList.keys())
      for key in keys:
        # get list of points for said colour, paint 10 items in list (gets X)
        cordList = self.masterList[key]
        for i in range(10):
          if not cordList:
            del self.masterList[key]
            break

          #pop our point and draw this point
          cord = cordList.pop(0)
          if self.switch == 1: # opening image
            paintColour = QColor(key)
            painter.setPen(paintColour)
          if self.switch == 2:  # connecting points
            paintColour = self.black
            painter.setPen(QPen(self.black, 
                                self.brushSize, 
                                Qt.SolidLine, 
                                Qt.RoundCap, 
                                Qt.RoundJoin
                                )
                          )
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
    self.pathList = {}
    image = self.pixMap.toImage()
    w = image.width()
    h = image.height()
    self.switch = 2
    self.createMasterList(image, w, h)

    # Loop through points we want to connect 
    i = 0
    size = len(self.startPointList)
    while i < size:
      if (i+1) == size:
        break
      self.Astar(self.startPointList[i],self.startPointList[i+1])
      i+=1
    
    # check if we have points to connect
    if size <=0:
      print('No Points Found')
    elif size==1:
      print('One point found')
    else: 
      self.masterList = self.pathList
      print('Connecting Points')
      self.autoPaint()

  def heuristic(self, x1, y1, x2, y2):
    h = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5 # eculedian distance
    return h
  
  def Astar(self, start, end):
    #set out masterlists and traversable colours
    masterMatrix = self.masterList
    traversableColours = [self.white, self.black] 


    # Initialize the A* search
    queue = [(0, start[0], start[1])] # (fScore, x, y) Lowest fScore will be at front
    cameFrom = {}
    gScore = {(start[0], start[1]): 0} #Dictonary to keep track of points we visted and their gScores
    fScore = {(start[0], start[1]): self.heuristic(*start, *end)} #Same as gScore expect for fScore
    while queue:
      f, x, y = heapq.heappop(queue)
      
      # if we hit our end point we add to our list of paths
      if (x,y) == end:
        path = [(x,y)]
        while (x, y) in cameFrom:
          x, y = cameFrom[(x, y)]
          path.append((x, y))
        self.pathList[x,y] = path[::-1]
        return
      
      #scoring loop
      for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
        # incement our point and check
        checkX, checkY = x+dx, y+dy
        
        if (checkX, checkY) in masterMatrix and masterMatrix[(checkX,checkY)] in traversableColours:
            # update scores
            tempGScore = gScore[(x, y)] + 1 # +1 as each point is one move
            if (checkX, checkY) not in gScore or tempGScore < gScore[(checkX, checkY)]:
                cameFrom[(checkX, checkY)] = (x, y) # update our path 
                gScore[(checkX, checkY)] = tempGScore
                fScore[(checkX, checkY)] = tempGScore + self.heuristic(checkX, checkY, *end)  
                heapq.heappush(queue, (fScore[(checkX, checkY)], checkX, checkY))    
    return 
  
