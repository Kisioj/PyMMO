import logging
import sys
import time
from collections import deque

import pygame
from glm import ortho, mat4
from pygame.constants import (
    K_LEFT,
    K_RIGHT,
    K_UP,
    K_DOWN,
    QUIT,
    KEYDOWN,
    KEYUP,
    K_ESCAPE,
    K_KP2,
    K_KP8,
    K_KP4,
    K_KP6,
    DOUBLEBUF, OPENGL)

from PyBYOND import step
from .base_types.mappable.movable.mob import Mob
from .base_types import world_map
from .base_types.client import Client
from .base_types.renderer import Renderer
from .base_types.world import World
from . import singletons as si

# from PyBYOND import api
from .verb import verbs


# si.client = Client()
# si.world = World()
# world_map.world = world
# SCREEN_WIDTH, SCREEN_HEIGHT = 400*2, 368*2

si.keyboard = {
    K_LEFT: False,
    K_RIGHT: False,
    K_UP: False,
    K_DOWN: False,
    K_KP4: False,
    K_KP6: False,
    K_KP8: False,
    K_KP2: False,
}


from OpenGL.GL import glClear, GL_COLOR_BUFFER_BIT, glViewport, glClearColor, glEnable, glDisable, glBlendFunc, GL_BLEND, \
    GL_DEPTH_TEST, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, glMatrixMode, glLoadIdentity, GL_QUADS, glBegin, glColor3f, glVertex2f, \
    glEnd, GL_MODELVIEW, GL_PROJECTION, glOrtho, glTranslatef, GL_TEXTURE_2D

map_object_attribute_types = {
    'density': lambda density: density == 'True'
}
BYONDtypes = world_map.WorldMap.types


FPS = 30


import types

si.world = World()
si.client = Client()
si.renderer = Renderer()


class PyBYOND(object):
    def update_viewport(self):
        view = si.world.view
        if isinstance(view, str):
            view_width, view_height = map(int, view.split('x'))
        elif isinstance(view, int):
            view = view * 2 + 1
            view_width, view_height = view, view
        else:
            raise TypeError('ERROR')

        icon_size = si.world.icon_size
        map_width = si.world.map.width
        map_height = si.world.map.height

        SCREEN_WIDTH, SCREEN_HEIGHT = (min(view_width, map_width) * icon_size), (min(view_height, map_height) * icon_size)

        si.world.screen_width = SCREEN_WIDTH  # TODO added
        si.world.screen_height = SCREEN_HEIGHT  # TODO added

        # si.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
        si.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DOUBLEBUF | OPENGL)


    def run(self):
        def spawned_function_time(spawned_function):
            run_time, function = spawned_function
            return run_time

        logging.info('verbs', verbs.items())
        world_map.WorldMap(si.world, 'map.ini')

        mob_class = si.world.mob or Mob
        player = mob_class()
        player.client = si.client
        si.client.mob = player
        si.client.eye = player

        player.__login__()

        pygame.init()
        pygame.font.init()
        fpsClock = pygame.time.Clock()
        pygame.display.set_caption('PyBomberman')

        self.update_viewport()

        count = 0
        fps_counter = deque()

        si.renderer.initialize()

        while True:
            now = time.perf_counter()
            fps_counter.append(now)
            while now - fps_counter[0] > 1:
                fps_counter.popleft()

            count += 1
            if count > 100:
                count = 0
                print('FPS', len(fps_counter))

            now_time = time.time()
            si.world.time = now_time
            for spawned_function in sorted(si.functions_queue, key=spawned_function_time):
                run_time, function = spawned_function

                if hasattr(function, '__self__') and function.__self__._deleted:
                    si.functions_queue.remove(spawned_function)
                elif now_time >= run_time:
                    si.functions_queue.remove(spawned_function)
                    if isinstance(function, types.GeneratorType):
                        try:
                            next(function)
                        except StopIteration:
                            pass
                    else:
                        function()
                else:
                    break

            for movable in si.gliding:
                movable.glide()

            player.handle_keyboard()

            # si.screen.fill((1, 0, 0))
            si.renderer.clear_screen()

            si.world.map.__draw__(si.world, si.client)

            for movable, walk_params in si.walking.items():
                if walk_params.ticks_left > 0:
                    walk_params.ticks_left -= 1
                else:
                    walk_params.ticks_left = walk_params.lag
                    step(movable, walk_params.direction)

            # player.draw()
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    si.client.__keydown__(event.key)
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN:
                    si.keyboard[event.key] = True
                elif event.type == KEYUP:
                    si.keyboard[event.key] = False

            # pygame.display.update()  # TODO use when not using OpenGL
            pygame.display.flip()  # TODO use with openGL
            fpsClock.tick(FPS)

pyBYOND = PyBYOND()

