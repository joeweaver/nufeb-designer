from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QMouseEvent, QPaintEvent, QPen, QPainter, QPixmap, QColor
from PyQt6.QtCore import Qt, QPoint
import numpy as np
import cv2 as cv2

# adapted from https://doc.qt.io/qtforpython-6.5/examples/example_widgets_painting_painter.html
class PaintingWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.x_microns = 100
        self.y_microns = 100
        self.scale = 5
        self.setFixedSize(self.x_microns*self.scale, self.y_microns*self.scale)
        self.pixmap = QPixmap(self.size())
        self.pixmap.fill()
        self.color = QColor("black")
        # TODO look into using the pixmap at the unscaled size and Qt.TransformationMode.FastTransformation
        self.unscaled_points = np.full((self.x_microns, self.y_microns), 0xFFFFFFFF, dtype=np.uint32)


    def clear_and_resize(self):
        #try to find the integer scaling that brings us closest to 500 pix for the longer dimension
        longest = max(self.x_microns,self.y_microns)
        self.scale = 500//longest
        self.setFixedSize(self.x_microns*self.scale, self.y_microns*self.scale)
        self.pixmap = QPixmap(self.size())
        self.pixmap.fill()
        self.color = QColor("black")
        # TODO look into using the pixmap at the unscaled size and Qt.TransformationMode.FastTransformation
        self.unscaled_points = np.full((self.x_microns, self.y_microns), 0xFFFFFFFF, dtype=np.uint32)
        self.update()

    def set_x(self, x_microns):
        self.x_microns = x_microns


    def set_y(self, y_microns):
        self.y_microns = y_microns

    def setColour(self,colour):
        self.color = colour

    def paintEvent(self, event: QPaintEvent):
        """Override method from QWidget

        Paint the Pixmap into the widget

        """
        with QPainter(self) as painter:
            painter.drawPixmap(0, 0, self.pixmap)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.draw_point(event.position().toPoint())
        elif event.button() == Qt.MouseButton.RightButton:
            self.erase_point(event.position().toPoint())

    def paint_point(self, point: QPoint, pen:QPen ):
        painter = QPainter(self.pixmap)
        pen.setWidth(self.scale)  # Set the point size
        painter.setPen(pen)
        clip = QPoint(round(point.x()//self.scale)*self.scale,round(point.y()//self.scale)*self.scale,)
        painter.drawPoint(clip)  # Draw the point on the pixmap

        self.unscaled_points[point.x()//self.scale,point.y()//self.scale]=pen.color().rgba()
        painter.end()  # End the painter
        self.update()  # Trigger a repaint to show the updated pixmap
        self.callback()

    def point_info(self):
        white = np.sum(self.unscaled_points == 0xFFFFFFFF)
        black = np.sum(self.unscaled_points == 0xFF000000)
        others = self.unscaled_points.size - black - white
        return white, black, others

    def erase_point(self, point: QPoint):
        pen = QPen(QColor("white"))  # Erasing is drawing white
        self.paint_point(point, pen)


    def draw_point(self, point: QPoint):
        pen = QPen(self.color)  # Set to colour of current taxon
        self.paint_point(point, pen)



    def save(self, filename: str):
        """ save pixmap to filename """
        #self.pixmap.save(f'scaled_{filename}')
        scaled_pixmap = self.pixmap.copy()  # Create a copy of the pixmap
        # Extract R, G, B channels from the uint32 values
        r = (self.unscaled_points >> 16) & 0xFF  # Extract the red channel
        g = (self.unscaled_points  >> 8) & 0xFF  # Extract the green channel
        b = self.unscaled_points  & 0xFF  # Extract the blue channel

        # Stack the channels to form an MxNx3 array
        rgb_array = np.stack((b, g, r), axis=-1).astype(np.uint8)  # Note: OpenCV uses BGR order
        rgb_array = np.transpose(rgb_array, (1, 0, 2))
        # Save the array as a PNG using OpenCV
        cv2.imwrite(filename, rgb_array)


    def load(self, filename: str):
        """ load pixmap from filename """
        self.pixmap.load(filename)
        self.pixmap = self.pixmap.scaled(self.size(), Qt.KeepAspectRatio)
        self.update()
        self.callback()

    def clear(self):
        """ Clear the pixmap """
        self.pixmap.fill(QColor("white"))
        self.unscaled_points = np.full((self.x_microns, self.y_microns), 0xFFFFFFFF, dtype=np.uint32)
        self.update()
        self.callback()

    def set_callback(self,fn):
        self.callback = fn