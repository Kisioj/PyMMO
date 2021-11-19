import logging
from collections import OrderedDict
from PIL import Image

import pygame

from .icon_state import IconState
from PyBYOND import singletons as si
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
                       GL_ACTIVE_UNIFORMS, glUniform1i, GL_RED)
from OpenGL.GLU import gluPerspective, gluLookAt
from OpenGL.arrays import vbo

from ..render.sprite_sheet import SpriteSheet
from ..render.texture import Texture

icon_key_types = {
    'width': int,
    'height': int,
    'state': str,
    'dirs': int,
    'frames': int,
    'delay': lambda delay: [int(x) for x in delay.split(',')],  # delay in 1/10s
    'loop': int,
}


class Icon(SpriteSheet):
    def __init__(self, filepath):
        super().__init__()
        self.filepath = filepath

        self.load_pixels_from_file(filepath)
        metadata = self.load_metadata(filepath)  # ALERT! sets self.tile_width, self.tile_height

        self.icon_states = OrderedDict()
        start_frame = 0
        for name, attrs in metadata:
            attrs = dict(attrs)
            icon_state = IconState(self, start_frame, name, **dict(attrs))
            self.icon_states[name] = icon_state
            start_frame += icon_state.total_frames

        self.initialized = False

    def initializeGL(self):
        self.initialized = True
        self.load_from_self_pixels()

    def scale(self, width, height):
        return
        """
        Scales tile size to width x height
        """
        # self.image = pygame.transform.scale(self.image, (width, height))
        # im.thumbnail Image.NEAREST

        for name, icon_state in self.icon_states.items():
            for i, frames in enumerate(icon_state.frames):
                icon_state.frames[i] = [
                    pygame.transform.scale(frame, (width, height))
                    for frame in frames
                ]
        logging.info('scale', width, height)

    def load_metadata(self, filepath):
        image = Image.open(filepath)
        desc = image.info.get('Description')
        logging.info(image.info)
        logging.info('desc', desc)
        image.close()

        icon_states_data = []
        state = None
        values = []
        for line in desc.split('\n')[2:-2]:
            if line.startswith('\t'):
                line = line.lstrip('\t')
                key, value = line.split(' = ')
                key_type = icon_key_types.get(key)
                if key_type:
                    value = key_type(value)

                if key == 'width':
                    self.tile_width = value
                elif key == 'height':
                    self.tile_height = value
                elif state is not None:
                    values.append((key, value))

            else:
                key, value = line.split(' = ')
                if key == 'state':
                    value = value.strip('"')
                if state is not None:
                    icon_states_data.append((state, values))
                state = value
                values = []

        if state is not None:
            icon_states_data.append((state, values))
        return icon_states_data



class IconDescriptor(object):
    def __set__(self, src, filepath):
        # print 'src', src, 'filename', filename
        if filepath not in si.icons:
            si.icons[filepath] = Icon(filepath)
        src._icon = si.icons[filepath]
        src._icon_state = src._icon.icon_states.get(src.icon_state, '')

    def __get__(self, src, cls):
        # print 'src', src, 'cls', cls
        # if issubclass(cls, type):
        #     return self
        icon = src._icon
        if src._icon:
            icon = icon.filepath
        return icon

