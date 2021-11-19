import numpy as np
from OpenGL.arrays import vbo
from OpenGL.GL import GL_ARRAY_BUFFER


class IconStateFrame:
    def __init__(self, rect, icon):
        self.rect = rect
        self.icon = icon

        clip_x, clip_y, clip_w, clip_h = rect
        tex_top = clip_y / icon.texture_height
        tex_bottom = (clip_y + clip_h) / icon.texture_height
        tex_left = clip_x / icon.texture_width
        tex_right = (clip_x + clip_w) / icon.texture_width
        quad_width = clip_w
        quad_height = clip_h

        vertices = np.array([
            0, 0, tex_left, tex_top,
            quad_width, 0, tex_right, tex_top,
            quad_width, quad_height, tex_right, tex_bottom,
            0, quad_height, tex_left, tex_bottom,
        ], dtype=np.float32)

        self.vbo = vbo.VBO(vertices, target=GL_ARRAY_BUFFER)
