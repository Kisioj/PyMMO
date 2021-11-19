import random
import sys

from OpenGL.arrays import vbo
from OpenGL.GL import GL_ELEMENT_ARRAY_BUFFER, glBindTexture, GL_TEXTURE_2D, glEnableClientState, GL_VERTEX_ARRAY, \
    GL_TEXTURE_COORD_ARRAY, GL_ARRAY_BUFFER, GL_FLOAT, glVertexPointer, glTexCoordPointer, glDrawElements, GL_QUADS, \
    GL_UNSIGNED_INT, glDisableClientState, glLoadIdentity, glTranslatef, GL_TRIANGLE_FAN, glClear, GL_COLOR_BUFFER_BIT, \
    glClearColor, glEnable, GL_BLEND, glDisable, GL_DEPTH_TEST, glBlendFunc, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, glViewport

import numpy as np
from glm import mat4, translate, vec3, ortho

import PyBYOND.singletons as si
from PyBYOND.base_types.shader_program import WaterShaderProgram, PickProgram


class Renderer:
    def __init__(self):
        self.ibo = vbo.VBO(np.array([
            0, 1, 2, 3
        ], dtype=np.int32), target=GL_ELEMENT_ARRAY_BUFFER)
        self.texture_id = None
        self.program = PickProgram()

    def initialize(self):

        # # Initialize Projection Matrix
        # glMatrixMode(GL_PROJECTION)
        # glLoadIdentity()
        # glOrtho(0.0, SCREEN_WIDTH, SCREEN_HEIGHT, 0.0, 1.0, -1.0)
        #
        # # Initialize Modelview Matrix
        # glMatrixMode(GL_MODELVIEW)
        # glLoadIdentity()


        self.program.load_program()
        self.program.bind()

        self.program.projection_matrix = ortho(0, si.world.screen_width, si.world.screen_height, 0)
        self.program.update_projection_matrix()

        self.program.model_view_matrix = mat4()
        self.program.update_model_view_matrix()

        self.program.unbind()

        glClearColor(0, 0, 0, 1)

        # glViewport(0, 0, si.world.screen_width, si.world.screen_height)  # TODO how come it works without this line? I guess pygame's set_mode runs this
        # glViewport(0, 0, 100, 100)

        glEnable(GL_BLEND)
        glDisable(GL_DEPTH_TEST)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glEnable(GL_TEXTURE_2D)



    def clear_screen(self):
        glClear(GL_COLOR_BUFFER_BIT)

    def before_render(self):
        self.program.enable_vertex_pointer()
        self.program.enable_tex_coord_pointer()
        # glEnableClientState(GL_VERTEX_ARRAY)
        # glEnableClientState(GL_TEXTURE_COORD_ARRAY)

    def render(self, frame, icon, x, y, atom):
        if not hasattr(atom, 'color'):
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)
            setattr(atom, 'color', (r, g, b))

        # glLoadIdentity()
        # glTranslatef(x, y, 0)
        self.program.bind()
        # self.program.model_view_matrix = mat4()
        self.program.model_view_matrix = translate(vec3(x, y, 0))
        self.program.update_model_view_matrix()

        # self.program.set_iPickColor(*atom.color)
        # self.program.set_iPickMode(1)

        if self.texture_id != icon.id:
            self.texture_id = icon.id
            glBindTexture(GL_TEXTURE_2D, icon.id)

        frame.vbo.bind()
        # glTexCoordPointer(2, GL_FLOAT, 16, frame.vbo + 8)
        # glVertexPointer(2, GL_FLOAT, 16, frame.vbo)

        self.program.set_vertex_pointer(16, frame.vbo)
        self.program.set_tex_coord_pointer(16, frame.vbo + 8)

        self.ibo.bind()
        glDrawElements(GL_TRIANGLE_FAN, 4, GL_UNSIGNED_INT, self.ibo)
        # glDrawElements(GL_QUADS, 4, GL_UNSIGNED_INT, self.ibo)

    def after_render(self):
        self.program.disable_vertex_pointer()
        self.program.disable_tex_coord_pointer()

        glBindTexture(GL_TEXTURE_2D, 0)

        # glDisableClientState(GL_VERTEX_ARRAY)
        # glDisableClientState(GL_TEXTURE_COORD_ARRAY)
