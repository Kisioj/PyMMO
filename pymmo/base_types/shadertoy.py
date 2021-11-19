import enum
import sys
import time
from copy import deepcopy, copy
from enum import Enum
from time import sleep
from collections import deque, namedtuple
from timeit import timeit

from OpenGL.GL import (glBegin, glEnd, glEnable, glColor3f, glClearColor, glVertex3f, glClear, glTranslatef, glMatrixMode,
                       glLoadIdentity, glPointSize, glLineWidth, GL_TRIANGLES, GL_COLOR_BUFFER_BIT,
                       GL_PROJECTION, GL_DEPTH_BUFFER_BIT, GL_MODELVIEW, GL_LINES, GL_DEPTH_TEST, glViewport, glOrtho, GL_QUADS,
                       glVertex2f, glPushMatrix, glPopMatrix, glGenTextures, GL_TEXTURE_2D, glBindTexture, glDeleteTextures,
                       GL_RGBA, glTexImage2D, GL_UNSIGNED_BYTE, GL_LINEAR, GL_TEXTURE_MAG_FILTER, glTexParameteri,
                       GL_TEXTURE_MIN_FILTER, glTexCoord2f, glGetTexImage, glTexSubImage2D, GL_BLEND, glDisable, glBlendFunc,
                       GL_ONE_MINUS_SRC_ALPHA, GL_SRC_ALPHA, glColor4f, GL_NEAREST, glRotate, glRotatef, glScalef, GL_REPEAT,
                       GL_TEXTURE_WRAP_S, GL_TEXTURE_WRAP_T, GL_TEXTURE, GL_CLAMP, GL_MIRRORED_REPEAT, GL_CLAMP_TO_EDGE,
                       GL_CLAMP_TO_BORDER, glEnableClientState, GL_VERTEX_ARRAY, GL_FLOAT, glVertexPointer, glDrawArrays,
                       glDisableClientState, glGenBuffers, glBindBuffer, GL_ARRAY_BUFFER, glBufferData, GL_STATIC_DRAW,
                       GL_ELEMENT_ARRAY_BUFFER, GL_UNSIGNED_INT, glDrawElements, GL_DYNAMIC_DRAW, GL_TEXTURE_COORD_ARRAY,
                       glBufferSubData, glTexCoordPointer, glDeleteBuffers, GL_TEXTURE_BUFFER, GL_ALPHA, GL_COLOR_ARRAY,
                       glColorPointer, glPolygonMode, GL_FRONT, GL_FILL, GL_LINE, GL_POINT, GL_POINTS, GL_LINE_STRIP,
                       GL_LINE_LOOP, GL_INT, GL_NOTEQUAL, glClearStencil, GL_STENCIL_BUFFER_BIT, glColorMask, GL_FALSE,
                       GL_STENCIL_TEST, glStencilFunc, GL_ALWAYS, glStencilOp, GL_REPLACE, GL_TRUE, GL_EQUAL, GL_KEEP,
                       glStencilMask, glGenFramebuffers, GL_FRAMEBUFFER, glBindFramebuffer, glFramebufferTexture2D,
                       GL_COLOR_ATTACHMENT0, glHint, GL_LINE_SMOOTH_HINT, GL_NICEST, GL_LINE_SMOOTH, GL_POLYGON_SMOOTH,
                       GL_MULTISAMPLE, GL_POLYGON_SMOOTH_HINT, glDeleteProgram, glUseProgram, glIsProgram, GL_INFO_LOG_LENGTH,
                       glGetProgramiv, glGetProgramInfoLog, glIsShader, glGetShaderiv, glGetShaderInfoLog, glCreateProgram,
                       GL_VERTEX_SHADER, glCreateShader, glShaderSource, glCompileShader, GL_COMPILE_STATUS, glAttachShader,
                       GL_FRAGMENT_SHADER, glLinkProgram, GL_LINK_STATUS, glDeleteShader, glGetUniformLocation, glUniform4f,
                       glUniformMatrix4fv, GL_TRIANGLE_FAN, glGetAttribLocation, glVertexAttribPointer, glEnableVertexAttribArray,
                       glDisableVertexAttribArray, glGetActiveAttrib, glGetActiveUniform, GL_ACTIVE_ATTRIBUTES,
                       GL_ACTIVE_UNIFORMS, glUniform1i, GL_RED, glUniform2i, glUniform2f, glUniform1f)
from OpenGL.GLU import gluPerspective, gluLookAt
from OpenGL.arrays import vbo
from PIL import Image

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtOpenGL
from PyQt5.QtCore import QBasicTimer
from PyQt5.QtGui import QImage, QOpenGLTexture
from PyQt5.QtOpenGL import QGLFormat
from PyQt5.QtWidgets import QApplication
import numpy as np
import freetype
from glm import mat4, value_ptr, ortho, orthoLH, translate, vec3, vec4

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 360

FPS = 60

FRAME_TIME_MS = 1000 / FPS  # ms/frame

Rect = namedtuple('Rect', ['x', 'y', 'w', 'h'])

DEFAULT_TEXTURE_WRAP = GL_REPEAT

gMouseX = 0
gMouseY = 0

start = time.perf_counter()


iResolution = SCREEN_WIDTH, SCREEN_HEIGHT

class MyTexture:
    def __init__(self):
        self.id = 0
        self.pixels = None

        self.texture_width = 0
        self.texture_height = 0
        self.image_width = 0
        self.image_height = 0
        self.vbo_id = 0
        self.ibo_id = 0

        self.vbo = None
        self.ibo = None

    def pad_pixels_32(self):
        if self.pixels is None:
            self.texture_width = self.next_power_of_two(self.image_width)
            self.texture_height = self.next_power_of_two(self.image_height)

            if self.texture_width != self.image_width or self.texture_height != self.image_height:
                zeros = np.zeros((self.texture_height, self.texture_width, 4), dtype=np.uint8)
                zeros[:self.image_height, :self.image_width, :] = self.pixels
                self.pixels = zeros

    def init_vbo(self):
        if self.vbo_id == 0 and self.id != 0:
            vertices = np.array([
                0, 0, 0, 0,
                0, 0, 0, 0,
                0, 0, 0, 0,
                0, 0, 0, 0,
            ], dtype=np.float32)

            indices = np.array([
                0, 1, 2, 3
            ], dtype=np.int32)

            # create VBO
            self.vbo_id = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, self.vbo_id)
            glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_DYNAMIC_DRAW)
            glBindBuffer(GL_ARRAY_BUFFER, 0)

            # create IBO
            self.ibo_id = glGenBuffers(1)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo_id)
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_DYNAMIC_DRAW)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

            print(f'{self.ibo_id=}')
            print(f'{self.vbo_id=}')

    def next_power_of_two(self, num):
        if num != 0:
            num -= 1
            num |= (num >> 1)
            num |= (num >> 2)
            num |= (num >> 4)
            num |= (num >> 8)
            num |= (num >> 16)
            num += 1
        return num

    def load_from_file(self, filepath):
        image = Image.open(filepath).convert('RGBA')
        self.pixels = np.array(image.getdata(), dtype=np.uint8).reshape(image.height, image.width, 4)

        self.image_width = image.width
        self.image_height = image.height

        self.texture_width = self.next_power_of_two(self.image_width)
        self.texture_height = self.next_power_of_two(self.image_height)

        if self.texture_width != self.image_width or self.texture_height != self.image_height:
            zeros = np.zeros((self.texture_height, self.texture_width, 4), dtype=np.uint8)
            zeros[:self.image_height, :self.image_width, :] = self.pixels
            self.pixels = zeros

        # generate texture id
        self.id = glGenTextures(1)

        glBindTexture(GL_TEXTURE_2D, self.id)

        # generate texture
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.texture_width, self.texture_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, self.pixels)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, DEFAULT_TEXTURE_WRAP)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, DEFAULT_TEXTURE_WRAP)

        glBindTexture(GL_TEXTURE_2D, 0)

        self.init_vbo()


    def render(self):
        if self.id == 0:
            return

        tex_top = 0
        tex_bottom = self.image_height# / self.texture_height
        tex_left = 0
        tex_right = self.image_width# / self.texture_width

        quad_width = self.image_width
        quad_height = self.image_height

        # x, y, s, t
        vertices = np.array([
            0, 0, tex_left, tex_top,
            quad_width, 0, tex_right, tex_top,
            quad_width, quad_height, tex_right, tex_bottom,
            0, quad_height, tex_left, tex_bottom,
        ], dtype=np.float32)

        indices = np.array([
            0, 1, 2, 3
        ], dtype=np.int32)

        glBindTexture(GL_TEXTURE_2D, self.id)

        gPolygonProgram.enable_vertex_pointer()
        gPolygonProgram.enable_tex_coord_pointer()


        my_ibo = vbo.VBO(indices, target=GL_ELEMENT_ARRAY_BUFFER)
        my_vbo = vbo.VBO(vertices, target=GL_ARRAY_BUFFER)

        my_vbo.bind()
        gPolygonProgram.set_vertex_pointer(16, my_vbo)
        gPolygonProgram.set_tex_coord_pointer(16, my_vbo + 8)

        my_ibo.bind()
        glDrawElements(GL_TRIANGLE_FAN, 4, GL_UNSIGNED_INT, my_ibo)

        gPolygonProgram.disable_vertex_pointer()
        gPolygonProgram.disable_tex_coord_pointer()


        glBindTexture(GL_TEXTURE_2D, 0)

gOpenGLTexure = MyTexture()
gTextColor = [1, 0.5, 1, 1]


class ShaderProgram:
    def __init__(self):
        self.id = 0

    def load_program(self):
        pass

    def free_program(self):
        glDeleteProgram(self.id)

    def bind(self):
        glUseProgram(self.id)

    def unbind(self):
        glUseProgram(0)


    def load_shader_from_file(self, filepath, shader_type):
        with open(filepath) as file:
            shader_source = file.read()

        shader_id = glCreateShader(shader_type)
        glShaderSource(shader_id, shader_source)
        glCompileShader(shader_id)
        if glGetShaderiv(shader_id, GL_COMPILE_STATUS) != GL_TRUE:
            print(f"Unable to compile shader ({filepath}):")
            self.print_shader_log(shader_id)
            glDeleteShader(shader_id)
            shader_id = 0

        return shader_id

    def print_program_log(self, program):
        if not glIsProgram(program):
            print("Invalid program")
            return

        info_log = glGetProgramInfoLog(program)
        print(f'{info_log=}')


    def print_shader_log(self, shader):
        if not glIsShader(shader):
            print("Invalid shader")
            return

        info_log = glGetShaderInfoLog(shader)
        print(f'{info_log=}')


class PlainPolygonProgram2D(ShaderProgram):
    def __init__(self):
        super().__init__()
        self.projection_matrix_location = 0
        self.projection_matrix = mat4()

        self.model_view_matrix_location = 0
        self.model_view_matrix = mat4()

        self.vertex_pos2d_location = 0
        self.tex_coord_location = 0
        self.tex_unit_location = 0

        self.iMouse = 0     # shadertoy: vec4, here: vec2
        self.iResolution = 0  # shadertoy: vec3, here: vec2

    def load_program(self):
        self.id = glCreateProgram()
        vertex_shader_id = self.load_shader_from_file("shadertoy.glvs", GL_VERTEX_SHADER)
        glAttachShader(self.id, vertex_shader_id)

        fragment_shader_id = self.load_shader_from_file("shadertoy.glfs", GL_FRAGMENT_SHADER)
        glAttachShader(self.id, fragment_shader_id)

        glLinkProgram(self.id)
        if glGetProgramiv(self.id, GL_LINK_STATUS) != GL_TRUE:
            print("Unable to link program:")
            self.print_program_log(self.id)
            glDeleteShader(vertex_shader_id)
            glDeleteShader(fragment_shader_id)
            glDeleteProgram(self.id)
            return

        # clean up shader references
        glDeleteShader(vertex_shader_id)
        glDeleteShader(fragment_shader_id)

        # attributes
        self.tex_coord_location = glGetAttribLocation(self.id, "VertTexCoord")
        self.vertex_pos2d_location = glGetAttribLocation(self.id, "VertexPos2D")
        # uniforms
        self.tex_unit_location = glGetUniformLocation(self.id, "TextureUnit")
        self.projection_matrix_location = glGetUniformLocation(self.id, "ProjectionMatrix")
        self.model_view_matrix_location = glGetUniformLocation(self.id, "ModelViewMatrix")

        self.iMouse = glGetUniformLocation(self.id, "iMouse")
        self.iResolution = glGetUniformLocation(self.id, "iResolution")
        self.iTime = glGetUniformLocation(self.id, "iTime")

        active_attributes = glGetProgramiv(self.id, GL_ACTIVE_ATTRIBUTES)
        print(f'{active_attributes=}')
        for i in range(active_attributes):
            print(f'{glGetActiveAttrib(self.id, i)}')

        active_uniforms = glGetProgramiv(self.id, GL_ACTIVE_UNIFORMS)
        print(f'{active_uniforms=}')
        for i in range(active_uniforms):
            print(f'{glGetActiveUniform(self.id, i)}')

    # def set_tex_color(self, r, g, b, a=1):
    #     glUniform4f(self.tex_color_location, r, g, b, a)

    def set_tex_unit(self, unit):
        glUniform1i(self.tex_unit_location, unit)

    def set_iMouse(self, x, y):
        glUniform2f(self.iMouse, x, y)

    def set_iResolution(self, w, h):
        glUniform2f(self.iResolution, w, h)

    def set_iTime(self, t):
        glUniform1f(self.iTime, t)

    def update_projection_matrix(self):
        glUniformMatrix4fv(self.projection_matrix_location, 1, GL_FALSE, value_ptr(self.projection_matrix))

    def update_model_view_matrix(self):
        glUniformMatrix4fv(self.model_view_matrix_location, 1, GL_FALSE, value_ptr(self.model_view_matrix))

    def set_vertex_pointer(self, stride, data):
        glVertexAttribPointer(self.vertex_pos2d_location, 2, GL_FLOAT, GL_FALSE, stride, data)

    def set_tex_coord_pointer(self, stride, data):
        glVertexAttribPointer(self.tex_coord_location, 2, GL_FLOAT, GL_FALSE, stride, data)

    def enable_vertex_pointer(self):
        glEnableVertexAttribArray(self.vertex_pos2d_location)

    def disable_vertex_pointer(self):
        glDisableVertexAttribArray(self.vertex_pos2d_location)

    def enable_tex_coord_pointer(self):
        glEnableVertexAttribArray(self.tex_coord_location)

    def disable_tex_coord_pointer(self):
        glDisableVertexAttribArray(self.tex_coord_location)


gPolygonProgram = PlainPolygonProgram2D()
gVBO = 0
gIBO = 0
gScreenArea = Rect(x=0, y=0, w=SCREEN_WIDTH, h=SCREEN_HEIGHT)


class OpenGLWidget(QtWidgets.QOpenGLWidget):

    def game_update(self):

        while self.key_events:
            event_name, key = self.key_events.popleft()
            if event_name in ('keyRelease',):
                if key == QtCore.Qt.Key_Q:
                    self.makeCurrent()
                    sec = timeit(stmt='self.paintGL()', globals={**globals(), 'self': self}, number=1000)
                    print(f'{sec=}')

            if event_name in ('keyPress', 'keyPressRepeated'):
                if key == QtCore.Qt.Key_Escape:
                    sys.exit(0)


    def initializeGL(self):
        print('initializeGL')
        self.load_gp()
        self.load_media()

        glViewport(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

        # Initialize clear color
        glClearColor(0, 0, 0, 1)

        # Enable texturing
        # glEnable(GL_TEXTURE_2D)

        # set blending
        glEnable(GL_BLEND)
        glDisable(GL_DEPTH_TEST)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT)

        gPolygonProgram.bind()
        gPolygonProgram.model_view_matrix = mat4()

        gPolygonProgram.set_iMouse(gMouseX, gMouseY)
        gPolygonProgram.set_iResolution(SCREEN_WIDTH, SCREEN_HEIGHT)
        gPolygonProgram.set_iTime(time.perf_counter()-start)

        gOpenGLTexure.render()

    def load_gp(self):
        gPolygonProgram.load_program()
        gPolygonProgram.bind()

        gPolygonProgram.projection_matrix = ortho(0, SCREEN_WIDTH, SCREEN_HEIGHT, 0)
        gPolygonProgram.update_projection_matrix()

        gPolygonProgram.model_view_matrix = mat4()
        gPolygonProgram.update_model_view_matrix()

        gPolygonProgram.set_tex_unit(0)
        gPolygonProgram.set_iMouse(384, 186)

    def load_media(self):
        gOpenGLTexure.load_from_file('rocks.jpg')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timer = QBasicTimer()
        self.timer.start(int(FRAME_TIME_MS), self)
        # self.setMouseTracking(True)

        self.fps_counter = deque()
        self.keys_pressed = set()
        self.key_events = deque()

    def timerEvent(self, event):
        now = time.perf_counter()
        self.fps_counter.append(now)
        while now - self.fps_counter[0] > 1:
            self.fps_counter.popleft()
        # print('FPS', len(self.fps_counter))
        self.game_update()
        self.update()

    def mouseMoveEvent(self, event):
        global gMouseX, gMouseY
        gMouseX = event.x()
        gMouseY = event.y()
        print('Mouse move {}: [{},{}]'.format(event.button(), event.x(), event.y()))

    def mousePressEvent(self, event):
        global gMouseX, gMouseY
        gMouseX = event.x()
        gMouseY = event.y()

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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = OpenGLWidget()

    format = widget.format()
    # format.setSamples(16)           # enable multisampling https://stackoverflow.com/questions/13713184/qglwidget-using-setformat-to-enable-multisampling-the-window-doesnt-close
    # format.setVersion(3, 2)
    widget.setFormat(format)

    widget.resize(SCREEN_WIDTH, SCREEN_HEIGHT)
    widget.show()
    app.exec_()

# water shader https://www.shadertoy.com/view/4ls3zj
# https://gamedev.stackexchange.com/questions/29672/in-out-keywords-in-glsl


# could still use GL_ALPHA instead of GL_RED : https://stackoverflow.com/questions/37027551/why-do-i-need-to-specify-image-format-as-gl-red-instead-of-gl-alpha-when-loading
