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
                       GL_ACTIVE_UNIFORMS, glUniform1i, GL_RED, glGenVertexArrays, glBindVertexArray)
from OpenGL.GLU import gluPerspective, gluLookAt
from OpenGL.arrays import vbo

from pymmo.render.texture import Texture
import numpy as np

class SpriteSheet(Texture):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clips = []
        self.vbo = None
        self.ibos = []

    def generate_data_buffer(self):
        if self.id != 0 and self.clips:

            tw, th = self.texture_width, self.texture_height
            clips = self.clips
            vertices = []

            for i, clip in enumerate(clips):
                indices = [
                    i * 4 + 0,
                    i * 4 + 1,
                    i * 4 + 2,
                    i * 4 + 3,
                ]
                ibo = vbo.VBO(np.array(indices, dtype=np.int32), target=GL_ELEMENT_ARRAY_BUFFER)
                self.ibos.append(ibo)

                v_top = 0
                v_bottom = clip.h
                v_left = 0
                v_right = clip.w

                vertices.extend([
                    v_left, v_top, clip.x / tw, clip.y / th,
                    v_right, v_top, (clip.x + clip.w) / tw, clip.y / th,
                    v_right, v_bottom, (clip.x + clip.w) / tw, (clip.y + clip.h) / th,
                    v_left, v_bottom, clip.x / tw, (clip.y + clip.h) / th,
                ])

            self.vbo = vbo.VBO(np.array(vertices, dtype=np.float32), target=GL_ARRAY_BUFFER)


    def delete_texture_if_exists(self):
        super().delete_texture_if_exists()
        if self.vbo:
            self.vbo.delete()
            self.vbo = None

        if self.ibos:
            for ibo in self.ibos:
                ibo.delete()
            self.ibos = []

        self.clips = []

    def render_sprite(self, index):
        if self.vbo is None:
            return

        ibo = self.ibos[index]

        glBindTexture(GL_TEXTURE_2D, self.id)

        self.program.enable_data_pointers()

        self.vbo.bind()
        self.program.set_vertex_pointer(16, self.vbo)

        ibo.bind()
        glDrawElements(GL_TRIANGLE_FAN, 4, GL_UNSIGNED_INT, ibo)

        self.program.disable_data_pointers()

        glBindTexture(GL_TEXTURE_2D, 0)

