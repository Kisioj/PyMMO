import configparser

from pymmo import constants
from pymmo import singletons as si
from .location import Location




class MappableTypesRegister:
    types = {}

    def __getitem__(self, type_name):
        return self.types[type_name]

    def __getattr__(self, type_name):
        return self.__getitem__(type_name)

    def add(self, cls):
        MappableTypesRegister.types[cls.__name__] = cls

    def __iter__(self):
        return self.types.keys()



# class Viewport:
#     def __init__(self, world, client):
#
#
#
#
#         eye = client.eye
#         view = client.view or world.view
#
#         view_width = view_height = 2
#
#         if isinstance(view, int):
#             view_width = view_height = 1 + (view * 2)
#         elif isinstance(view, str):
#             view_width, view_height = view.split('x')
#             view_width = int(view_width)
#             view_height = int(view_height)
#
#
#         eye_x, eye_y = eye.x, eye.y
#         from_x = max(0, eye_x - view_width // 2)
#         from_y = max(0, eye_y - view_height // 2)
#
#
#         # | | | | | | 5
#         # | | | | | | 4
#         # | | |X| | | 3
#         # | | | | | | 2
#         # | | | | | | 1
#         #  1 2 3 4 5
#         # 5coord, 2view
#



class WorldMap:
    types = MappableTypesRegister()

    def __init__(self, world, filename):
        world.map = self
        config = configparser.ConfigParser()
        if not config.read(filename):
            raise Exception(f"Cannot read config file '{filename}'")
        raw_map = config.get('level', 'map').split('\n')
        self.width, self.height = len(raw_map[0]), len(raw_map)

        self.fields = [[[] for _ in range(self.width)] for _ in range(self.height)]
        for y in range(self.height):
            for x in range(self.width):
                cell = self.fields[y][x]

                symbol = raw_map[self.height - y - 1][x]
                cell_conent = config.get('level', symbol)
                if ', ' in cell_conent:
                    cell_conent = cell_conent.split(', ')
                else:
                    cell_conent = [cell_conent]

                for atom_type in cell_conent:
                    WorldMap.types[atom_type](x=x, y=y)

    def __draw__(self, world, client):
        # world.view
        # client.view
        # client.eye.loc

        # TODO add perspective
        # •MOB_PERSPECTIVE
        # •EYE_PERSPECTIVE
        # •EDGE_PERSPECTIVE

        # we should draw one more tile than view because of the
        # 0 - real 1x1, take into account 3x3
        # 1 - real 3x3, take into account 5x5
        # 2 - real 5x5, take into account 7x7

        si.renderer.before_render()

        to_draw = []
        for y in range(self.height):
            for x in range(self.width):
                for atom in self.fields[y][x]:
                    to_draw.append(atom)

        to_draw.sort(key=lambda atom: atom.layer)
        for atom in to_draw:
            atom.draw()

        si.renderer.after_render()

    # def locate(self, x, y, z=1):  # probably should also give possibility to pass class Turf argument here, z
    #     return Location(x, y)
