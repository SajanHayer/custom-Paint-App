from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
import operator
#custom files
from buttonColour import QPaletteButton, COLORS
from canvasPaint import paintWindow

BRUSHSIZES = [1, 4, 7, 9, 12]
FILEACTIONS = ['Save', 'Open', 'Clear', 'Connect']

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        #set our window/widgets
        widget = QWidget()
        layout = QVBoxLayout()  # one item on top of another
        widget.setLayout(layout)

        # creating menu bar
        mainMenu = self.menuBar()
        self.menuHeight = mainMenu.height()
        self.fileMenu = mainMenu.addMenu("File")
        self.addFileButtons()
        self.brushMenu = mainMenu.addMenu("Brush Size")
        self.addSizeButtons()

        layout.addWidget(mainMenu)

        palette = QHBoxLayout()
        self.addPaletteButtons(palette)
        layout.addLayout(palette)

        self.canvas = paintWindow()
        layout.addWidget(self.canvas)
        self.setCentralWidget(widget)

    def addPaletteButtons(self, layout):
      for c in COLORS:
        button = QPaletteButton(c)
        button.pressed.connect(lambda c=c: self.canvas.changeBrushColour(c))
        layout.addWidget(button)

    def addSizeButtons(self):
      for size in BRUSHSIZES:
        s = str(size)
        action  = QAction(s+"px", self) #button 
        action.triggered.connect(lambda checked, size=size: self.canvas.changeBrushSize(size))
        self.brushMenu.addAction(action) #button -> menu
    
    def addFileButtons(self):
      for action in FILEACTIONS:
        a = QAction(action, self)
        action = action.lower()
        a.triggered.connect(lambda checked, action=action: operator.methodcaller(action, self)(MainWindow))
        self.fileMenu.addAction(a)

    def save(self):
      self.canvas.save()

    def open(self):
      self.canvas.open()

    def clear(self):
      self.canvas.clear()

    def connect(self):
      self.canvas.connect()


       




app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
