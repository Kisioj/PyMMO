import logging
# from pygame.constants import (
#     K_LEFT,
#     K_RIGHT,
#     K_UP,
#     K_DOWN,
#     K_KP4,
#     K_KP6,
#     K_KP8,
#     K_KP2
# )

from PySide6.QtCore import Qt
K_LEFT = Qt.Key_Left
K_RIGHT = Qt.Key_Right
K_UP = Qt.Key_Up
K_DOWN = Qt.Key_Down
K_KP4 = Qt.Key_4
K_KP6 = Qt.Key_6
K_KP8 = Qt.Key_8
K_KP2 = Qt.Key_2

from pymmo.base_types.atom import Atom
from pymmo.constants import (
    SOUTH,
    NORTH,
    WEST,
    EAST,
)
from pymmo import singletons as si
from pymmo.api import (
    get_step,
)


class Movable(Atom):
    _is_gliding = False
    glide_size = 4

    def glide(self):
        if self._is_gliding:
            x, y = self.x, self.y
            glide_size = self.glide_size
            to_screen_x = x * si.world.icon_size
            to_screen_y = (si.world.map.height - y) * si.world.icon_size
            if self._screen_x < to_screen_x:
                self._screen_x += glide_size
            elif self._screen_x > to_screen_x:
                self._screen_x -= glide_size

            if self._screen_y < to_screen_y:
                self._screen_y += glide_size
            elif self._screen_y > to_screen_y:
                self._screen_y -= glide_size

            if self._screen_x == to_screen_x and self._screen_y == to_screen_y:
                self._is_gliding = False
                si.gliding.remove(self)

    def handle_keyboard(self):
        if self in si.walking:
            del si.walking[self]

        key_up = si.keyboard[K_UP] or si.keyboard[K_KP8]
        key_down = si.keyboard[K_DOWN] or si.keyboard[K_KP2]
        key_right = si.keyboard[K_RIGHT] or si.keyboard[K_KP6]
        key_left = si.keyboard[K_LEFT] or si.keyboard[K_KP4]

        movements = (
            (key_up and not key_down, NORTH),
            (key_down and not key_up, SOUTH),
            (key_right and not key_left, EAST),
            (key_left and not key_right, WEST),
        )

        for condition, direction in movements:
            if condition:
                self.Move(
                    location=get_step(ref=self, direction=direction),
                    direction=direction
                )
                logging.info('MOVED {} {}'.format(self.x, self.y))
                break


    def Move(self, location, direction):
        self.dir = direction

        dense_object = [
            obj
            for obj in location
            if obj.density is True
        ]
        if dense_object:
            self.Bump(dense_object[0])
        else:
            if not self.loc.Exit(self, location):
                return
            if not location.Enter(self, self.loc):
                return
            self.loc.Exited(self, location)
            location.Entered(self, self.loc)

            world_map = si.world.map.fields
            world_map[self.y][self.x].remove(self) ## jakos to inaczej zrobic, zby to sie w setterze robilo samo x, y

            if self._is_gliding:
                si.gliding.remove(self)
                self._screen_x = self.x * si.world.icon_size
                self._screen_y = (si.world.map.height - self.y) * si.world.icon_size

            self.x, self.y = location.x, location.y
            world_map[self.y][self.x].append(self) ## jakos to inaczej zrobic, zby to sie w setterze robilo samo x , y
            self._is_gliding = True
            si.gliding.append(self)

    def Bump(self, obstacle):
        logging.info(self, 'bumps into', obstacle)
