# importing libraries
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
import heapq
from PIL import Image

# INTIAL CODE FRAMEWORK REFERENCED FROM:  
# https://www.geeksforgeeks.org/pyqt5-create-paint-application/
# Made changes to add A* algorithm to connect points together on the app
#

class Window(QMainWindow):
  #constructor
  def __init__(self):
    super().__init__()

    # setting title
    self.setWindowTitle("Paint App")
   
    # setting geometry to main window
    self.maxSize = (1000,800)
    self.setGeometry(
                      100, 
                      100, 
                      self.maxSize[0],
                      self.maxSize[1]
                    )


    # Change our Cursor Image 
    cursorImage = QPixmap('cursorPencil.png')
    cursor = QCursor(cursorImage, 0, cursorImage.height())
    self.setCursor(cursor)

    redButton = QPushButton('Red')
    # layout = QBoxLayout()
    # layout.addWidget(redButton)

    # drawing flag
    self.drawing = False

    # default brush size and colour, lastpoint
    self.brushSize = 1
    self.brushColor = Qt.black
    self.lastPoint = QPoint()

    # creating menu bar
    mainMenu = self.menuBar()
    self.menuHeight = mainMenu.height()
    # addiding menues to the main menu
    self.fileMenu = mainMenu.addMenu("File")
    self.brushMenu = mainMenu.addMenu("Brush Size")
    self.colourMenu = mainMenu.addMenu("Brush Color")

    # functions to add buttons
    self.addSizeButtons()
    self.addColourButtons()
    self.addFileButtons()

      # creating image object
    # self.image = QImage(self.size(), QImage.Format_RGB32)
    self.image = QImage(self.maxSize[0]-100, self.maxSize[1]-self.menuHeight, QImage.Format_RGB32)
    self.image.fill(Qt.white)

#---------------------------END OF CONSTRUCTOR--------------------------
  
  def animate(self):
    # PyQt has the functionality to add a timer to your window which allows for some pretty cool things 
    # we can update our window every 10 milliseconds to create an animation of drawing an image. 
    # what this function does is it starts our timer and sets the time limit -> 10ms
    # after 10ms it calls the function we specified in our timeout functionality
    self.timer.start(10)

  #-----------------------------------ADD BUTTONS-----------------------
  def addSizeButtons(self):
    """
    Adds size buttons to the brush menu.

    This function creates four action buttons (4px, 7px, 9px, and 12px) and adds them to the `self.brushMenu` menu. Each button is connected to a corresponding `setBrushSize()` method call, which sets the brush size to the specified value.

    The purpose of this function is to provide the user with a visual selection of brush sizes that can be easily chosen from the brush menu.

    Returns:
        None
    """
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
  
  def addColourButtons(self):
    """
    Adds color buttons to the color menu.

    This function creates five action buttons (Black, White, Green, Yellow, and Red) and adds them to the `self.colourMenu` menu. Each button is connected to a corresponding `changeColour()` method call, which sets the drawing color to the specified value.

    The purpose of this function is to provide the user with a visual selection of colors that can be easily chosen from the color menu.

    Returns:
        None
    """
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
 
  def addFileButtons(self):
    """
    Adds file-related buttons to the file menu.

    This function creates three action buttons: "Save", "Clear", and "Connect Points". These buttons are added to the `self.fileMenu` menu.

    The "Save" button is connected to the `self.save` method, which is responsible for saving the user's drawing. The "Clear" button is connected to the `self.clear` method, which clears the drawing canvas. The "Connect Points" button is connected to the `self.connectPoints` method, which draws lines between the points the user has drawn.

    The purpose of this function is to provide the user with a set of common file-related actions that can be easily accessed from the file menu.

    Returns:
        None
    """
    # creating save action
    saveAction = QAction("Save", self)
    saveAction.setShortcut("Ctrl + S") # adding short cut for save action
    self.fileMenu.addAction(saveAction)
    saveAction.triggered.connect(self.save)

    # creating clear action
    clearAction = QAction("Clear", self)
    self.fileMenu.addAction(clearAction)
    clearAction.triggered.connect(self.clear)

    openAction = QAction("Open", self)
    self.fileMenu.addAction(openAction)
    openAction.triggered.connect(self.open)
    #draw points button 
    connectPointButton = QAction('Connect Points', self)
    self.fileMenu.addAction(connectPointButton)
    connectPointButton.triggered.connect(self.connectPoints)
  #-----------------------------------ADD BUTTONS-----------------------
  

  #-----------------------------------BUTTON ACTIONS--------------------
  def save(self):
    """
    Saves the current state of the canvas to a file.

    The supported file formats for saving are PNG (*.png), JPEG (*.jpg, *.jpeg), and all files (*.*).

    This method is typically called when the user wants to save the current state of the canvas to a file, such as by clicking a "Save" button or menu item in the application.
    """
    filePath, _ = QFileDialog.getSaveFileName(self, "Save Image", "",
                      "PNG(*.png);;JPEG(*.jpg *.jpeg);;All Files(*.*) ")

    if filePath == "":
        return
    self.image.save(filePath)

  def open(self):
    #opens file exporler
    name, _ = QFileDialog.getOpenFileName(self, 'Open File', "",
                                       "PNG(*.png);;JPEG(*.jpg *.jpeg)" ) 
    if name:
      self.clear()
      print('Opening Image')
      # if image is valied we open usign PILLOW and get width and height
      openImage = Image.open(name)
      w, h = openImage.size
      # check if the opened image has a bigger size than our screen, 
      # we resize accordinly 
      if (w*h)>((self.maxSize[0]-100)*(self.maxSize[1]-self.menuHeight)):
        # resize image but maintaing aspect ratio
        openImage.thumbnail(self.maxSize)
      # create masterList and paint our image
      self.masterList = self.createDictonaryOrList(openImage, openImageFlag=True)
      self.automatePaint(openImageFlag=True)

  def clear(self):
    """
    Method to clear the canvas
    """
    # make the whole canvas white
    self.image.fill(Qt.white)
    # update
    self.update()

  def setBrushSize(self, size):
    """
    Method to change brush size
    Size (int) -> Size of new brush (in Pixels)
    """
    self.brushSize = size

  def changeColour(self, colour):
    """
    Method to change the colour of the brush 

    Colour (String (all lowercase)) -> Name of the
                                       colour we want to change to
    """
    try:
        color_attr = getattr(Qt, colour)
        self.brushColor = color_attr
    except AttributeError:
        # Handle the case where the color name is not found
        self.brushColor = Qt.black
  #-----------------------------------BUTTON ACTIONS--------------------


  #----------------------------------MOUSE EVENTS-----------------------
  def mousePressEvent(self, event):
    """
    Handles the mouse press event for drawing on the canvas.
    The `self.mouseDraw()` function is responsible for actually drawing 
    on the canvas based on the mouse events.

    Args: 
      event (QMouseEvent):  The mouse event object that contains 
                            information about the mouse press, 
                            such as the cursor position 
                            and button that was pressed.

    """
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
      
  def mouseMoveEvent(self, event):
    """
    Handles the mouse move event for drawing on the canvas.
    The `self.mouseDraw()` function is responsible for actually drawing 
    on the canvas based on the mouse events.

    Args:
      event (QMouseEvent):  The mouse event object that contains 
                            information about the current mouse 
                            position and button states.
    """
    # checking if left button is pressed and drawing flag is true
    if (event.buttons() & Qt.LeftButton) & self.drawing:
      self.mouseDraw(
        draw=event,
        position=self.lastPoint,
        drag=True
      )

  def mouseReleaseEvent(self, event):
    """
    Handles the mouse release event for drawing on the canvas.
    This function is called when the user releases the left mouse button. 
    Args:
      event (QMouseEvent):  The mouse event object that contains 
                            information about the mouse release, 
    """
    if event.button() == Qt.LeftButton:
        # make drawing flag false
        self.drawing = False

  def mouseDraw(self, draw, position, drag=False):
    """
    Draws on the canvas based on mouse events.

    Args:
      draw (QMouseEvent): The mouse event object that contains 
                          information about the current mouse position.
      position (QPoint): The last recorded mouse position.
      drag (bool, optional):  Indicates whether the user is dragging 
                              the mouse while drawing. Defaults to `False`.
    """
    # creating painter object
    painter = QPainter(self.image)
    
    self.lastPoint = QPoint(self.lastPoint.x(), self.lastPoint.y()-self.menuHeight)
    drawPoint = QPoint(draw.pos().x(), draw.pos().y()-self.menuHeight)

    # set the pen of the painter
    painter.setPen(QPen(self.brushColor, self.brushSize, 
                    Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

    # if drag is True, the mouse is clicked and moving so we draw from 
    # point to point 
    if drag:
      painter.drawLine(self.lastPoint, drawPoint)
    # else we are just clicking so draw at that point
    else:
      painter.drawPoint(self.lastPoint)
      # creating painter object

    # change the last point and update the the image
    self.lastPoint = draw.pos()  
    self.update()
  
  def paintEvent(self, event):
    """
    Handles the paint event for the canvas.

    Args:
        event (QPaintEvent): The paint event object that contains 
        information about the area of the canvas that needs to be redrawn.
    """
    # create a canvas
    canvasPainter = QPainter(self)
    # draw rectangle  on the canvas
    canvasPainter.drawImage(0, self.menuHeight, self.image) # x,y image 
    # canvasPainter.drawImage(self.rect(), self.image, self.image.rect())


  #----------------------------------MOUSE EVENTS-----------------------


  #----------------------------DIFFERENT COLOURING FUNCATIONALITY-------
  def heuristic(self, x1, y1, x2, y2):
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
  
  def getPath(self, start, end):
    """
    Function that uses A* algorithm to find the best path between two 
    given points (Start, end)

    Start (tuple) -> A tuple that contains the starting coordinates
    End (tuple) -> A tuple that contains the ending coordinates
    """
    # Create a dictionary to store the 2D matrix data
    masterMatrix = {(x, y): color for x, y, color in self.masterList}

    traversableColor = [Qt.white, Qt.black] 

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
        path = [(x,y)]
        while (x, y) in cameFrom:
          x, y = cameFrom[(x, y)]
          path.append((x, y))
        self.pathList.append(path[::-1])
        return
      
      # check each direction for the current point we are on to see if 
      # which point we should move to next
      for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
      # for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
        # get the points surronding our current point 
        checkX, checkY = x+dx, y+dy
        # check if our new point is in the masterMatrix dictonary and 
        # then if that point is a traversable colour using the same matrix
        if (checkX, checkY) in masterMatrix and masterMatrix[(checkX,checkY)] in traversableColor:
            # get the gScore of our orginal x, y point and +1 to it 
            # as we have moved (left, right, up, down or diagonally)
            tempGScore = gScore[(x, y)] + 1 # +1 as each point is one move

            # check if the value we moved to is NOT in our gScore dictonary 
            # or if our current score is lower than the Score we have moved to 
            # we check gscore as fscore includes the calculation of which point is closer throwing off the algorithm 
            if (checkX, checkY) not in gScore or tempGScore < gScore[(checkX, checkY)]:
                cameFrom[(checkX, checkY)] = (x, y) # update our path 
                # update our score dicatonaries with the temp score we calculated 
                # and the heurisitc calculation as well 
                gScore[(checkX, checkY)] = tempGScore

                # wallScore = self.distance_to_wall(checkX, checkY, masterMatrix)
                 # *end -> unpacks the tuple and sends it to the function
                fScore[(checkX, checkY)] = tempGScore + self.heuristic(checkX, checkY, *end) 
                # push all the points we checked into our queue, with their fScore and point value
                heapq.heappush(queue, (fScore[(checkX, checkY)], checkX, checkY))
    
    return 

  def colourPath(self):
    """
    Handles the drawing of paths on the canvas.

    This function is responsible for the following:

    1. Checking if there are any paths available to be drawn, either in the `self.pathList` or `self.currentPath`.
    2. If there are paths available, it determines which path to draw next based on the `self.changePath` flag.
    3. If there is a current path to draw, it creates a QPainter object, sets the pen color and size, and draws the next point in the path on the `self.image` canvas.
    4. After drawing a point, it updates the canvas to display the changes.
    5. If the `self.currentPath` is empty, it sets the `self.changePath` flag to True to switch to the next path in `self.pathList`.
    6. If both `self.pathList` and `self.currentPath` are empty, it stops the timer that triggers this function.

    This function is typically called repeatedly by a timer or other mechanism to continuously draw the paths on the canvas.
    """
    # check if either our list of paths or our current path is not empty 
    # we continue to draw 
    if len(self.pathList)>0 or len(self.currentPath)>0:
      # change which path we are drawing
      if self.changePath:
        self.currentPath = self.pathList.pop(0)
        
      # if our current path is not empty we continue drawing
      if len(self.currentPath)>0:
        self.changePath = False
        # create painter object
        painter = QPainter(self.image)
        painter.setPen(QPen(Qt.black, self.brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

        # get the current point we have to draw in our path and change it to a Qpoint
        # we have to unpack the tuple that is returned so we use *
        point = QPoint(*self.currentPath.pop(0))

        # draw our point, update the window and increment to next point
        painter.drawPoint(point)
        self.update()
      else: #when empth we change paths
        self.changePath = True

    # stop the timer when both our current path and list of paths are empty
    else:
      self.timer.stop()

  def connectPoints(self):
    """
    Connects the black points in the image using the A* algorithm.

    This function performs the following steps:

    1. Initializes the `self.listColoursPoints` list to store the coordinates of the black points in the image.
    2. Initializes the `self.masterList` list to store the color information for each pixel in the image.
    3. Initializes the `self.pathList` list to store the paths between the black points.
    

    This function is responsible for the initial setup and preprocessing of the image data, as well as the setup of the timer and path drawing logic.
    """

    #set lists
    self.listColoursPoints = []
    self.masterList = []
    self.pathList = []

    
    # Loop Through each pixel in image and get the colour and point
    self.masterList = self.createDictonaryOrList(self.image)

    # Loop through points we want to connect 
    i = 0
    while i < len(self.listColoursPoints):
      if (i+1) == len(self.listColoursPoints):
        break
      # print(self.listColoursPoints[i],self.listColoursPoints[i+1])
      self.getPath(self.listColoursPoints[i],self.listColoursPoints[i+1])
      i+=1
    size = len(self.listColoursPoints)


    if size <=0:
      print('No Points Found')
    elif size==1:
      print('One point found')
    else: 
      # paint our paths
      print('Connecting Points')
      self.automatePaint()

  def colourImage(self):
    print('How many times we get called')
    # LOOP REFERENCED FROM PREVIOUS CODE I CREATED 'animateImage.py'
    if len(self.masterList)>0:
      painter = QPainter(self.image)
      # this draws the whole thing, we want to be able to keep track of where we are as well as make sure we dont copy the last 
      # we can use a counter/timer or something to create this, either when a colour ends or keep track of a count then cancel

      colourKeys = list(self.masterList.keys())
      for colour in colourKeys:
        cordList = self.masterList[colour]
        for i in range(10):
          if not cordList:
            del self.masterList[colour]
            break
          cord = cordList.pop(0)
          #get color based on rgb key in masterDict
          paintColour = QColor(*colour)
          painter.setPen(paintColour)
          painter.drawPoint(*cord)
          i+=1

      # End the painting and update the label
      painter.end()
      self.update()
    else:
      print('----------')
      self.timer.stop()


  def automatePaint(self, openImageFlag=False):
    # create a timer object for our window
    self.timer = QTimer(self)
    
    if openImageFlag:
      print(openImageFlag)
      self.timer.timeout.connect(self.colourImage)
    else:  
      # connect the timeout of this timer to call a function
      self.timer.timeout.connect(self.colourPath)

    # set our checks and current path
    self.changePath = True
    self.currentPath = [1]

    # start our timer 
    self.animate()

  def createDictonaryOrList(self, image, openImageFlag=False):
    if openImageFlag: # if we are openign an image change what we are creating
      width, height = image.size
      masterList = {}
    else: # we use () an lists if we are connecting points
      height = image.height()
      width = image.width()
      masterList = []

    # Loop through the given image and get each coordinate and Colour value
    for y in range(height):
      for x in range(width):

        if openImageFlag: #we open picture and get each pixel, cord and colour
          colourVal = image.getpixel((x,y))
          # masterList.append((x,y,colourVal))
          if colourVal not in masterList:
            masterList[colourVal]=[(x,y)]
          else:
            masterList[colourVal].append((x,y))

        else:  #open our canvas and we get each pixel, cord and colour
          colour = QColor(self.image.pixel(x,y))
          masterList.append((x,y,colour))
          if colour == Qt.black:
            self.listColoursPoints.append((x,y))

    return masterList
  
    #----------------------------------CONNECT POINT FUNCATIONALITY-------


# TODO: UI OVERHAULED
  # TODO: Add our functions for connecting points 
  # TODO: Add brushchange and menue functionality
# TODO: Figure out the ability to change traversable colours, walls, and add 
        # text explaining?
# TODO: Change way to connect points -> less pixel dense, or buffer of 10 px in normal
  # TODO: Fix menu to change how connect points works if we do this ^
# TODO: Fix visual stuff 
  # TODO: Canvas is in middle of screen with borders around (just like paint)
  # TODO: Change Colour -> Colour wheel?, colour squares 
  # TODO: Ability to resize
# TODO: Create optimized path finding (this means we would change our algo)
# TODO: Docstring for remainging funcitons



if __name__ == "__main__":
  App = QApplication(sys.argv)
  
  # create the instance of our Window
  window = Window()
  
  # showing the window
  window.show()
  
  # start the app
  sys.exit(App.exec())