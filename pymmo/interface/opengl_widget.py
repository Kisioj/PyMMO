import sys
from time import sleep

from OpenGL.GL import (glBegin, glEnd, glEnable, glColor3f, glClearColor, glVertex3f, glClear, glTranslatef, glMatrixMode,
                       glLoadIdentity, glPointSize, glLineWidth, GL_TRIANGLES, GL_COLOR_BUFFER_BIT,
                       GL_PROJECTION, GL_DEPTH_BUFFER_BIT, GL_MODELVIEW, GL_LINES, GL_DEPTH_TEST, glViewport, glOrtho, GL_QUADS,
                       glVertex2f)
from OpenGL.GLU import gluPerspective, gluLookAt

from PySide6 import QtWidgets
from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtOpenGL
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QApplication

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
# aspect = SCREEN_WIDTH / SCREEN_HEIGHT

COLOR_MODE_CYAN = 1
COLOR_MODE_MULTI = 2

gColorMode = COLOR_MODE_MULTI



class OpenGLWidget(QOpenGLWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.parent = parent
        # self.setMouseTracking(True)

    def mouseMoveEvent(self, evt):
        print('Mouse move {}: [{},{}]'.format(evt.button(), evt.x(), evt.y()))

    def mousePressEvent(self, evt):
        print('Mouse press {}: [{},{}]'.format(evt.button(), evt.x(), evt.y()))

    def mouseReleaseEvent(self, evt):
        print('Mouse release {}: [{},{}]'.format(evt.button(), evt.x(), evt.y()))

    def keyPressEvent(self, evt):
        print('Key press {}'.format(evt.key()))

    def keyReleaseEvent(self, evt):
        print('Key release {}'.format(evt.key()))

    def initializeGL(self):
        print('initializeGL')
        # Initialize Projection Matrix
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0.0, SCREEN_WIDTH, SCREEN_HEIGHT, 0.0, 1.0, -1.0)

        # Initialize Modelview Matrix
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Initialize clear color
        glClearColor(1, 0, 0, 1)

    def paintGL(self):
        glViewport(0, 0, 100, 100)
        # print('paintGL')
        # Clear color buffer
        glClear(GL_COLOR_BUFFER_BIT)

        # Reset modelview matrix
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Move to center of the screen
        glTranslatef(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 0)

        # RYGB Mix
        glBegin(GL_QUADS)
        glColor3f(1, 0, 0)
        glVertex2f(-50, -50)
        glColor3f(1, 1, 0)
        glVertex2f(50, -50)
        glColor3f(0, 1, 0)
        glVertex2f(50, 50)
        glColor3f(0, 0, 1)
        glVertex2f(-50, 50)
        glEnd()

    def resizeGL(self, width, height):
        # print(f'{width=}, {height=}')
        # print(self.width(), 'x', self.height())
        # glViewport(0, 0, 100, 100)
        pass
        glOrtho(0.0, width, height, 0.0, 1.0, -1.0)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = OpenGLWidget()
    widget.resize(SCREEN_WIDTH, SCREEN_HEIGHT)
    widget.show()
    app.exec_()
