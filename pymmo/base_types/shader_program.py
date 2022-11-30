from OpenGL.GL import GL_LINK_STATUS, GL_TRUE, glAttachShader, glCreateProgram, glLinkProgram, glGetProgramiv, glDeleteShader, \
    glGetAttribLocation, glGetUniformLocation, GL_VERTEX_SHADER, GL_FRAGMENT_SHADER, GL_ACTIVE_ATTRIBUTES, GL_ACTIVE_UNIFORMS, \
    glGetActiveAttrib, glGetActiveUniform, glUniform1f, glUniform2f, glUniform1i, glUniformMatrix4fv, glVertexAttribPointer, \
    glEnableVertexAttribArray, glDisableVertexAttribArray, GL_FALSE, GL_FLOAT, glDeleteProgram, glUseProgram, glShaderSource, \
    glCompileShader, glGetShaderiv, glIsProgram, glGetProgramInfoLog, glIsShader, glGetShaderInfoLog, glCreateShader, \
    GL_COMPILE_STATUS, glUniform3i
from glm import value_ptr, mat4
import os


VERTEX_SHADER = """
# version 330
layout(location = 0) in vec2 VertexPos2D;
layout(location = 1) in vec2 VertTexCoord;

uniform mat4 ProjectionMatrix;
uniform mat4 ModelViewMatrix;

out vec2 FragTexCoord;
void main()
{
    gl_Position = ProjectionMatrix * ModelViewMatrix * vec4(VertexPos2D.x, VertexPos2D.y, 0.0, 1.0);
    FragTexCoord = VertTexCoord;
}
"""

FRAGMENT_SHADER = """
# version 330
in vec2 FragTexCoord;
out vec4 glFragColor;

uniform sampler2D TextureUnit;
uniform ivec3 iPickColor;
uniform int iPickMode;

void main()
{
    if(iPickMode == 0){

        glFragColor = texture(TextureUnit, FragTexCoord);
        //glFragColor = vec4(0.5, 0.0, 0.0, 1.0);
    }else{
        vec4 tmpColor = texture(TextureUnit, FragTexCoord);
        //if (tmpColor.a <= 0.0) discard;
        float alpha = 1.0;
        if (tmpColor.a <= 0.0) {
            alpha = 0.0;
        }
        glFragColor = vec4(iPickColor.r/255.0, iPickColor.g/255.0, iPickColor.b/255.0, alpha);
    }
}
"""

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

    def load_shader_from_text(self, shader_source, shader_type):
        shader_id = glCreateShader(shader_type)
        glShaderSource(shader_id, shader_source)
        glCompileShader(shader_id)
        if glGetShaderiv(shader_id, GL_COMPILE_STATUS) != GL_TRUE:
            print(f"Unable to compile shader:")
            print(shader_source)
            self.print_shader_log(shader_id)
            glDeleteShader(shader_id)
            shader_id = 0

        return shader_id

    def load_shader_from_file(self, filepath, shader_type):
        with open(filepath) as file:
            shader_source = file.read()

        return self.load_shader_from_text(shader_source=shader_source, shader_type=shader_type)

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


class PickProgram(ShaderProgram):
    def __init__(self):
        super().__init__()
        self.projection_matrix_location = 0
        self.projection_matrix = mat4()

        self.model_view_matrix_location = 0
        self.model_view_matrix = mat4()

        self.vertex_pos2d_location = 0
        self.tex_coord_location = 0
        self.tex_unit_location = 0

        self.iPickColor = None  # (0, 0, 0)
        self.iPickMode = None   # 0
        self.ENABLE_PICK_MODE = 0

    def load_program(self):
        self.id = glCreateProgram()
        print(f'{self.id=}')
        # vertex_shader_id = self.load_shader_from_file(os.path.join(os.path.dirname(__file__), 'basic.glvs'), GL_VERTEX_SHADER)
        vertex_shader_id = self.load_shader_from_text(VERTEX_SHADER, GL_VERTEX_SHADER)
        glAttachShader(self.id, vertex_shader_id)

        # fragment_shader_id = self.load_shader_from_file(os.path.join(os.path.dirname(__file__), 'basic.glfs'), GL_FRAGMENT_SHADER)
        fragment_shader_id = self.load_shader_from_text(FRAGMENT_SHADER, GL_FRAGMENT_SHADER)
        glAttachShader(self.id, fragment_shader_id)

        glLinkProgram(self.id)
        if glGetProgramiv(self.id, GL_LINK_STATUS) != GL_TRUE:
            print("1Unable to link program:")
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

        self.iPickColor = glGetUniformLocation(self.id, "iPickColor")
        self.iPickMode = glGetUniformLocation(self.id, "iPickMode")

        active_attributes = glGetProgramiv(self.id, GL_ACTIVE_ATTRIBUTES)
        print(f'{active_attributes=}')
        for i in range(active_attributes):
            print(f'{glGetActiveAttrib(self.id, i)}')

        active_uniforms = glGetProgramiv(self.id, GL_ACTIVE_UNIFORMS)
        print(f'{active_uniforms=}')
        for i in range(active_uniforms):
            print(f'{glGetActiveUniform(self.id, i)}')

    def set_tex_unit(self, unit):
        glUniform1i(self.tex_unit_location, unit)

    def set_iPickColor(self, r, g, b):
        glUniform3i(self.iPickColor, r, g, b)

    def set_iPickMode(self, mode):
        glUniform1i(self.iPickMode, mode)

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


class WaterShaderProgram(ShaderProgram):
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
        # vertex_shader_id = self.load_shader_from_file("/home/kisioj/PycharmProjects/pybomberman/pymmo/base_types/basic.glvs", GL_VERTEX_SHADER)
        vertex_shader_id = self.load_shader_from_file("/home/kisioj/PycharmProjects/pybomberman/pymmo/base_types/shadertoy.glvs", GL_VERTEX_SHADER)
        glAttachShader(self.id, vertex_shader_id)

        # fragment_shader_id = self.load_shader_from_file("/home/kisioj/PycharmProjects/pybomberman/pymmo/base_types/basic.glfs", GL_FRAGMENT_SHADER)
        fragment_shader_id = self.load_shader_from_file("/home/kisioj/PycharmProjects/pybomberman/pymmo/base_types/shadertoy.glfs", GL_FRAGMENT_SHADER)
        glAttachShader(self.id, fragment_shader_id)

        glLinkProgram(self.id)
        if glGetProgramiv(self.id, GL_LINK_STATUS) != GL_TRUE:
            print("2Unable to link program:")
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
