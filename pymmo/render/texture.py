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

import numpy as np
from PIL import Image


class Texture:
    def __init__(self):
        self.id = 0
        self.pixels = None
        self.alpha_pixels = None
        self.pixel_format = None

        self.texture_width = 0
        self.texture_height = 0
        self.image_width = 0
        self.image_height = 0
        self.vbo_id = 0
        self.ibo_id = 0

        self.vbo = None
        self.ibo = None

        self.program = None

    def create_pixels_32(self, width, height):
        if width <= 0 or height <= 0:
            return

        self.delete_texture_if_exists()

        self.pixels = np.zeros((height, width, 4), dtype=np.uint8)

        self.image_width = width
        self.image_height = height
        self.texture_width = width
        self.texture_height = height

        self.pixel_format = GL_RGBA

    def copy_pixels_32(self, pixels, width, height):
        if width <= 0 or height <= 0:
            return

        self.delete_texture_if_exists()

        zeros = np.zeros((height, width, 4), dtype=np.uint8)
        zeros[:height, :width, :] = pixels
        self.pixels = zeros

        self.image_width = width
        self.image_height = height
        self.texture_width = width
        self.texture_height = height

        self.pixel_format = GL_RGBA

    def pad_pixels_32(self):
        if self.pixels is None:
            self.texture_width = self.next_power_of_two(self.image_width)
            self.texture_height = self.next_power_of_two(self.image_height)

            if self.texture_width != self.image_width or self.texture_height != self.image_height:
                zeros = np.zeros((self.texture_height, self.texture_width, 4), dtype=np.uint8)
                zeros[:self.image_height, :self.image_width, :] = self.pixels
                self.pixels = zeros


    def blit_pixels_32(self, x, y, dest):
        if self.pixels is None or dest.pixels is None:
            return

        dest.pixels[y:y+self.image_height, x:x+self.image_width, :] = self.pixels[:self.image_height, :self.image_width]


    def create_pixels_8(self, width, height):
        if width <= 0 or height <= 0:
            return

        width = int(width)
        height = int(height)

        self.delete_texture_if_exists()

        self.pixels = np.zeros((height, width), dtype=np.uint8)

        self.image_width = width
        self.image_height = height
        self.texture_width = width
        self.texture_height = height

        self.pixel_format = GL_RED

    def copy_pixels_8(self, pixels, width, height):
        if width <= 0 or height <= 0:
            return

        self.delete_texture_if_exists()

        zeros = np.zeros((height, width), dtype=np.uint8)
        zeros[:height, :width] = pixels
        self.pixels = zeros

        self.image_width = width
        self.image_height = height
        self.texture_width = width
        self.texture_height = height

        self.pixel_format = GL_RED

    def pad_pixels_8(self):
        if self.pixels is None:
            self.texture_width = self.next_power_of_two(self.image_width)
            self.texture_height = self.next_power_of_two(self.image_height)

            if self.texture_width != self.image_width or self.texture_height != self.image_height:
                zeros = np.zeros((self.texture_height, self.texture_width), dtype=np.uint8)
                zeros[:self.image_height, :self.image_width] = self.pixels
                self.pixels = zeros

    def blit_pixels_8(self, x, y, dest):
        if self.pixels is None or dest.pixels is None:
            return

        x = int(x)
        y = int(y)
        try:
            print(f'{self.image_height=}, {self.image_width=}, {self.pixels.shape=}')
            print(f'{dest.image_height=}, {dest.image_width=}, {dest.pixels.shape=}')
            print(f'dest.pixels[{y}:{y + self.image_height}, {x}:{x + self.image_width}] = self.pixels')
            print(f'{y=}, {x=}\n')
            dest.pixels[y:y + self.image_height, x:x + self.image_width] = self.pixels
        except ValueError:
            raise

    # def lock(self):
    #     if self.pixels is None and self.id != 0:
    #         # size = self.texture_width * self.texture_height
    #         # self.pixels = np.array(size, dtype=np.uint32)
    #
    #         # set current texture
    #         glBindTexture(GL_TEXTURE_2D, self.id)
    #         #
    #         # # get pixels
    #         pixels = glGetTexImage(GL_TEXTURE_2D, 0, self.pixel_format, GL_UNSIGNED_BYTE)
    #         self.pixels = np.frombuffer(pixels, dtype=np.uint8).reshape(self.texture_width, self.texture_height,
    #                                                                     4).copy()  # if we dont copy, we wont be able to modify
    #         # self.pixels = np.fromstring(pixels, dtype='>u4')
    #         # self.pixels = np.fromstring(pixels, dtype='>u4')
    #         #
    #         # unbind texture
    #         glBindTexture(GL_TEXTURE_2D, 0)
    #
    #         return True
    #     return False
    #
    # def unlock(self):
    #     if self.pixels is not None and self.id != 0:
    #         # set current texture
    #         glBindTexture(GL_TEXTURE_2D, self.id)
    #
    #         # get pixels
    #         glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, self.texture_width, self.texture_height, self.pixel_format, GL_UNSIGNED_BYTE,
    #                         self.pixels)
    #
    #         self.pixels = None
    #
    #         # unbind texture
    #         glBindTexture(GL_TEXTURE_2D, 0)
    #         return True
    #
    #     return False

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

    def load_pixels_8_from_file(self, filepath):
        def rgb2gray(rgb):
            r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
            gray = 0.299 * r + 0.587 * g + 0.114 * b
            return gray.astype(np.uint8)

        self.delete_texture_if_exists()

        image = Image.open(filepath).convert('RGBA')
        self.pixels = np.array(image.getdata(), dtype=np.uint8).reshape(image.height, image.width, 4)

        self.pixels = rgb2gray(pixels)

        self.image_width = image.width
        self.image_height = image.height

        self.texture_width = self.next_power_of_two(self.image_width)
        self.texture_height = self.next_power_of_two(self.image_height)

        if self.texture_width != self.image_width or self.texture_height != self.image_height:
            zeros = np.zeros((self.texture_height, self.texture_width), dtype=np.uint8)
            zeros[:self.image_height, :self.image_width] = self.pixels
            self.pixels = zeros

        return self.pixels


    def load_pixels_from_file(self, filepath):
        self.delete_texture_if_exists()

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

        return self.pixels

    def load_from_file(self, filepath, colorkey: tuple = None, pixel_format=GL_RGBA):
        if pixel_format == GL_RGBA:
            pixels = self.load_pixels_from_file(filepath)
        elif pixel_format == GL_RED:
            pixels = self.load_pixels_8_from_file(filepath)

        if colorkey:
            transparent = (255, 255, 255, 0)

            # replace colorkey with transparent
            for y in range(self.texture_height):
                for x in range(self.texture_width):
                    if all(pixels[y, x] == colorkey):
                        pixels[y, x, :] = transparent

        self.load_from_pixels(pixels, pixel_format=pixel_format)

    def load_from_self_pixels(self, pixel_format=GL_RGBA):
        self.load_from_pixels(self.pixels, pixel_format=pixel_format)

    def load_from_pixels(self, pixels, pixel_format=GL_RGBA):
        self.pixels = pixels

        self.id = glGenTextures(1)

        if glGetError() != GL_NO_ERROR:
            print("ERROR")
            sys.exit(1)

        glBindTexture(GL_TEXTURE_2D, self.id)

        # generate texture
        glTexImage2D(GL_TEXTURE_2D, 0, pixel_format, self.texture_width, self.texture_height, 0, pixel_format, GL_UNSIGNED_BYTE, pixels)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

        glBindTexture(GL_TEXTURE_2D, 0)

        self.init_vbo()

        self.pixel_format = pixel_format


    def delete_texture_if_exists(self):
        if self.id != 0:
            glDeleteTextures(1, [self.id])
            self.id = 0
        if self.vbo_id:
            glDeleteBuffers(1, self.vbo_id)
            self.vbo_id = 0
        if self.ibo_id:
            glDeleteBuffers(1, self.ibo_id)
            self.ibo_id = 0

        self.texture_width = 0
        self.texture_height = 0
        self.image_width = 0
        self.image_height = 0

    def render(self, x, y, clip=None):
        if self.id == 0:
            return

        tex_top = 0
        tex_bottom = self.image_height / self.texture_height
        tex_left = 0
        tex_right = self.image_width / self.texture_width

        quad_width = self.image_width
        quad_height = self.image_height

        if clip:
            tex_top = clip.y / self.texture_height
            tex_bottom = (clip.y + clip.h) / self.texture_height
            tex_left = clip.x / self.texture_width
            tex_right = (clip.x + clip.w) / self.texture_width
            quad_width = clip.w
            quad_height = clip.h

        # move to the rendering point
        self.program.model_view_matrix = translate(vec3(x, y, 0)) * self.program.model_view_matrix
        self.program.update_model_view_matrix()

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

        self.program.enable_vertex_pointer()
        self.program.enable_tex_coord_pointer()

        my_ibo = vbo.VBO(indices, target=GL_ELEMENT_ARRAY_BUFFER)
        my_vbo = vbo.VBO(vertices, target=GL_ARRAY_BUFFER)

        my_vbo.bind()
        self.program.set_vertex_pointer(16, my_vbo)
        self.program.set_tex_coord_pointer(16, my_vbo + 8)

        my_ibo.bind()
        glDrawElements(GL_TRIANGLE_FAN, 4, GL_UNSIGNED_INT, my_ibo)

        self.program.disable_vertex_pointer()
        self.program.disable_tex_coord_pointer()

        glBindTexture(GL_TEXTURE_2D, 0)
