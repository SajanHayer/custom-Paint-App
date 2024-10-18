from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

# Code refrenced from: https://www.pythonguis.com/tutorials/bitmap-graphics/

COLORS = [
# 17 undertones https://lospec.com/palette-list/17undertones
'#000000', '#141923', '#414168', '#3a7fa7', '#35e3e3', '#8fd970', '#5ebb49',
'#458352', '#dcd37b', '#fffee5', '#ffd035', '#cc9245', '#a15c3e', '#a42f3b',
'#f45b7a', '#c24998', '#81588d', '#bcb0c2', '#ffffff',
]


class QPaletteButton(QPushButton):
  def __init__(self, color):
    super().__init__()
    self.setFixedSize(QSize(24,24))
    self.color = color
    self.setStyleSheet("background-color: %s;" % color)
  