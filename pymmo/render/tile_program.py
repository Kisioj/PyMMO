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

from glm import mat4, value_ptr, ortho, orthoLH, translate, vec3, vec4

from pymmo.render.shader_program import ShaderProgram


class TileProgram(ShaderProgram):
    def __init__(self):
        super().__init__()
        self.projection_matrix_location = 0
        self.projection_matrix = mat4()

        self.model_view_matrix_location = 0
        self.model_view_matrix = mat4()

        self.vertex_pos2d_location = 0
        self.tex_coord_location = 0
        self.tex_color_location = 0
        self.tex_unit_location = 0

    def load_program(self):
        self.id = glCreateProgram()
        vertex_shader_id = self.load_shader_from_file("shader.glvs", GL_VERTEX_SHADER)
        glAttachShader(self.id, vertex_shader_id)

        fragment_shader_id = self.load_shader_from_file("shader.glfs", GL_FRAGMENT_SHADER)
        glAttachShader(self.id, fragment_shader_id)

        glLinkProgram(self.id)
        if glGetProgramiv(self.id, GL_LINK_STATUS) != GL_TRUE:
            print("4Unable to link program:")
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
        self.tex_color_location = glGetUniformLocation(self.id, "TextureColor")
        self.tex_unit_location = glGetUniformLocation(self.id, "TextureUnit")
        self.projection_matrix_location = glGetUniformLocation(self.id, "ProjectionMatrix")
        self.model_view_matrix_location = glGetUniformLocation(self.id, "ModelViewMatrix")

        active_attributes = glGetProgramiv(self.id, GL_ACTIVE_ATTRIBUTES)
        print(f'{active_attributes=}')
        for i in range(active_attributes):
            print(f'{glGetActiveAttrib(self.id, i)}')

        active_uniforms = glGetProgramiv(self.id, GL_ACTIVE_UNIFORMS)
        print(f'{active_uniforms=}')
        for i in range(active_uniforms):
            print(f'{glGetActiveUniform(self.id, i)}')

    def set_tex_color(self, r, g, b, a=1):
        glUniform4f(self.tex_color_location, r, g, b, a)

    def set_tex_unit(self, unit):
        glUniform1i(self.tex_unit_location, unit)

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
