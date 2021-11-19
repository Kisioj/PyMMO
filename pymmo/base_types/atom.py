import logging
import sys
import time

from .icon_state import IconStateDescriptor
from .mappable_meta import MappableMeta
import numpy as np
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
                       GL_ACTIVE_UNIFORMS, glUniform1i, GL_RED, GL_NO_ERROR, glGetError)
from OpenGL.GLU import gluPerspective, gluLookAt
from OpenGL.arrays import vbo

from PyBYOND import constants
from PyBYOND.base_types.icon import IconDescriptor
from PyBYOND import singletons as si

DIR_TO_DIR_INDEX_MAP = {
    constants.SOUTH: constants.SOUTH_INDEX,
    constants.NORTH: constants.NORTH_INDEX,
    constants.WEST: constants.WEST_INDEX,
    constants.EAST: constants.EAST_INDEX,
}


class Atom(metaclass=MappableMeta):
    _icon = ''
    _icon_state = ''
    icon = IconDescriptor()
    icon_state = IconStateDescriptor()
    x = 0
    y = 0
    z = 0
    density = False

    layer = 0
    pixel_x = 0
    pixel_y = 0

    _dir = constants.SOUTH
    _dir_index = constants.SOUTH_INDEX
    _frame_no = 0
    _loop_no = 0  # how many loops animation has done
    _time_diff = 0
    _deleted = False

    _is_gliding = False  # atoms cannot move but need this object for icon with movable states

    def __repr__(self):
        return 'the {}'.format(self.__class__.__name__.lower())

    @property
    def dir(self):
        return self._dir

    @dir.setter
    def dir(self, direction):
        self._dir = direction
        self._dir_index = DIR_TO_DIR_INDEX_MAP[direction]

    def __init__(self, x=None, y=None):
        self.name = self.__class__.__name__.lower()
        self._last_time = time.time()
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
        self._screen_x = self.x * si.world.icon_size
        self._screen_y = (si.world.map.height - self.y) * si.world.icon_size
        si.world.map.fields[self.y][self.x].append(self)

        self.dots = 1

    def __remove__(self):
        if self not in si.world.map.fields[self.y][self.x]:
            logging.info(self, self.x, self.y, si.world.map.fields[self.y][self.x])
        assert self in si.world.map.fields[self.y][self.x]
        si.world.map.fields[self.y][self.x].remove(self)
        self._deleted = True
        if self in si.walking:
            del si.walking[self]

    @property
    def loc(self):
        from PyBYOND import base_types  # FIXME circular import
        return base_types.Location(self.x, self.y, self.z)

    def draw(self):
        if self.icon:
            self.animate()
            self.render()

    def animate(self):
        icon_state = self._icon_state
        try:
            frames_count = icon_state._frames_count
        except AttributeError:
            raise

        # animate_more = icon_state.attr_loop == constants.INFINITE or self._loop_no < icon_state.attr_loop

        if frames_count > 1:
            is_animation_on = True
            movement_animation = icon_state.attr_movement
            if movement_animation and not self._is_gliding:
                is_animation_on = False
            if is_animation_on:
                if icon_state.attr_loop != constants.INFINITE and self._loop_no >= icon_state.attr_loop:
                    return
                now_time = si.world.time
                self._time_diff += now_time - self._last_time
                last_time_diff = self._time_diff
                self._last_time = now_time

                total_delay_in_seconds = icon_state.total_delay / 10.0
                current_delay_in_seconds = icon_state.delay[self._frame_no] / 10.0

                if self._time_diff > total_delay_in_seconds:
                    self._time_diff %= total_delay_in_seconds
                    self._loop_no += 1
                    logging.info('ROUGH')

                changed_frame = False
                while self._time_diff > current_delay_in_seconds:
                     current_delay_in_seconds = icon_state.delay[self._frame_no] / 10.0
                     self._time_diff -= current_delay_in_seconds
                     self._frame_no += 1
                     self._frame_no %= icon_state._frames_count
                     changed_frame = True
                     if self._frame_no == (icon_state._frames_count - 1):
                         self._loop_no += 1

                if movement_animation and changed_frame:
                     logging.info('frame: {}, time_diff: {}, si.world.time: {}, delay_in_sec: {}, total_delay_in_sec: {}'.format(self._frame_no, last_time_diff, now_time, current_delay_in_seconds, total_delay_in_seconds))
            else:
                if movement_animation:
                    self._loop_no = 0
                    self._frame_no = 0
                    self._last_time = si.world.time
                    sys.stdout.write('\r' + ((self.dots // 100) + 1) * '.')
                    self.dots += 1
                    if self.dots >= 300:
                        self.dots = 1

    def render(self):
        if self.icon:

            dir_index = self._dir_index if self._dir_index < self._icon_state.attr_dirs else 0
            frame = self._icon_state.frames[dir_index][self._frame_no]


            eye = si.client.eye

            camera_center_x = eye._screen_x + 16
            camera_center_y = eye._screen_y + 16
            camera_top_left_x = camera_center_x - si.world.screen_width // 2
            camera_top_left_y = camera_center_y - si.world.screen_height // 2

            left = self._screen_x - camera_top_left_x + self.pixel_x
            top = self._screen_y - camera_top_left_y + self.pixel_y

            if not self._icon.initialized:
                self._icon.initializeGL()

            si.renderer.render(frame, self._icon, left, top, self)


    def Enter(self, movable, old_location):
        logging.info(self, "__Enter__")
        return True

    def Entered(self, movable, old_location):
        logging.info(self, "__Entered__")
        return True

    def Exit(self, movable, new_location):
        logging.info(self, "__Exit__")
        return True

    def Exited(self, movable, new_location):
        logging.info(self, "__Exited__")
        return True
