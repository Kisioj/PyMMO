import logging
import sys
import types
from collections import deque
import time

from OpenGL.GL import (glBegin, glEnd, glEnable, glColor3f, glClearColor, glVertex3f, glClear, glTranslatef, glMatrixMode,
                       glLoadIdentity, glPointSize, glLineWidth, GL_TRIANGLES, GL_COLOR_BUFFER_BIT,
                       GL_PROJECTION, GL_DEPTH_BUFFER_BIT, GL_MODELVIEW, GL_LINES, GL_DEPTH_TEST, glViewport, glOrtho, GL_QUADS,
                       glVertex2f)
from OpenGL.GLU import gluPerspective, gluLookAt

from PySide6 import QtWidgets
from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtOpenGL
from PySide6.QtCore import QBasicTimer, Qt
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QApplication


from pymmo import singletons as si, step, Mob
from pymmo.base_types import world_map
from pymmo.verb import verbs

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
# aspect = SCREEN_WIDTH / SCREEN_HEIGHT

COLOR_MODE_CYAN = 1
COLOR_MODE_MULTI = 2

gColorMode = COLOR_MODE_MULTI

FPS = 60
FRAME_TIME_MS = 1000 / FPS


class OpenGLWidget(QOpenGLWidget):
    def update_viewport(self):
        view = si.world.view
        if isinstance(view, str):
            view_width, view_height = map(int, view.split('x'))
        elif isinstance(view, int):
            view = view * 2 + 1
            view_width, view_height = view, view
        else:
            raise TypeError('ERROR')

        icon_size = si.world.icon_size
        map_width = si.world.map.width
        map_height = si.world.map.height

        SCREEN_WIDTH, SCREEN_HEIGHT = (min(view_width, map_width) * icon_size), (min(view_height, map_height) * icon_size)

        si.world.screen_width = SCREEN_WIDTH  # TODO added
        si.world.screen_height = SCREEN_HEIGHT  # TODO added


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timer = QBasicTimer()
        self.timer.start(int(FRAME_TIME_MS), self)
        # self.setMouseTracking(True)
        self.fps_counter = deque()
        self.keys_pressed = set()
        self.key_events = deque()

        self.count = 0

        logging.info('verbs', verbs.items())
        # TODO powinno map.ini przyjść po sieci
        # tak jak informacje o turfach i innych, nie?

        # w sumie nie, bo to jest kod backendu właśnie... hmmm...
        world_map.WorldMap(si.world, 'map.ini')

        mob_class = si.world.mob or Mob
        self.player = mob_class()
        self.player.client = si.client
        si.client.mob = self.player
        si.client.eye = self.player

        self.player.__login__()

        self.update_viewport()


    def timerEvent(self, event):
        now = time.perf_counter()
        self.fps_counter.append(now)
        while now - self.fps_counter[0] > 1:
            self.fps_counter.popleft()
        # print('FPS', len(self.fps_counter))
        self.game_update()
        self.update()

    def spawned_function_time(self, spawned_function):
        run_time, function = spawned_function
        return run_time

    def game_update(self):


        now = time.perf_counter()
        self.fps_counter.append(now)
        while now - self.fps_counter[0] > 1:
            self.fps_counter.popleft()

        self.count += 1
        if self.count > 100:
            self.count = 0
            print('FPS', len(self.fps_counter))


        now_time = time.time()
        si.world.time = now_time
        for spawned_function in sorted(si.functions_queue, key=self.spawned_function_time):
            run_time, function = spawned_function

            if hasattr(function, '__self__') and function.__self__._deleted:
                si.functions_queue.remove(spawned_function)
            elif now_time >= run_time:
                si.functions_queue.remove(spawned_function)
                if isinstance(function, types.GeneratorType):
                    try:
                        next(function)
                    except StopIteration:
                        pass
                else:
                    function()
            else:
                break


        for movable in si.gliding:
            movable.glide()

        self.player.handle_keyboard()

        # si.renderer.clear_screen()
        #
        # si.world.map.__draw__(si.world, si.client)

        for movable, walk_params in si.walking.items():
            if walk_params.ticks_left > 0:
                walk_params.ticks_left -= 1
            else:
                walk_params.ticks_left = walk_params.lag
                step(movable, walk_params.direction)

        while self.key_events:
            event_name, key = self.key_events.popleft()
            if event_name in ('keyPress',):
                print(f'{event_name=}, {key=}')
                si.keyboard[key] = True
                si.client.__keydown__(key)
                if key == QtCore.Qt.Key_Escape:
                    sys.exit(0)

            if event_name in ('keyRelease',):
                print(f'{event_name=}, {key=}')
                si.keyboard[key] = False

    def mouseMoveEvent(self, event):
        global gMouseX, gMouseY
        gMouseX = event.x()
        gMouseY = event.y()
        print('Mouse move {}: [{},{}]'.format(event.button(), event.x(), event.y()))

    def mousePressEvent(self, event):
        global gMouseX, gMouseY
        gMouseX = event.x()
        gMouseY = event.y()
        print(self.hasFocus())
        print(self.focusPolicy())
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

        print('Mouse press {}: [{},{}]'.format(event.button(), event.x(), event.y()))

    def mouseReleaseEvent(self, event):
        print('Mouse release {}: [{},{}]'.format(event.button(), event.x(), event.y()))

    def keyPressEvent(self, event):
        if event.isAutoRepeat():
            self.key_events.append(('keyPressRepeated', event.key()))
        else:
            self.key_events.append(('keyPress', event.key()))

    def keyReleaseEvent(self, event):
        if event.isAutoRepeat():
            self.key_events.append(('keyReleaseRepeated', event.key()))
        else:
            self.key_events.append(('keyRelease', event.key()))

    def initializeGL(self):
        si.renderer.initialize()

    def paintGL(self):
        si.renderer.clear_screen()
        si.world.map.__draw__(si.world, si.client)

    def resizeGL(self, width, height):
        pass



if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = OpenGLWidget()
    widget.resize(SCREEN_WIDTH, SCREEN_HEIGHT)
    widget.show()
    app.exec_()
