import logging

from pymmo import (
    api,
    constants,
    singletons as si,
)


sounds = {}


class Client(object):
    def __init__(self):
        self.mob = None
        self.controls = {}
        self.eye = None
        self.view = None


    def __keydown__(self, key):
        # print 'Client.__kedown__', key, verbs.items()
        if key in self.controls:
            self.controls[key](self.mob)

    def __keyup__(self, key):
        pass

    def play(self, filename):
        return
        #
        # if filename not in sounds:
        #     sounds[filename] = pygame.mixer.Sound(filename)
        # sounds[filename].play()
        # logging.info(filename, 'plays')

    def __north__(self):
        self.mob.Move(loc=api.get_step(self.mob, constants.NORTH), direction=constants.NORTH)

    def __south__(self):
        self.mob.Move(loc=api.get_step(self.mob, constants.SOUTH), direction=constants.SOUTH)

    def __east__(self):
        self.mob.Move(loc=api.get_step(self.mob, constants.EAST), direction=constants.EAST)

    def __west__(self):
        self.mob.Move(loc=api.get_step(self.mob, constants.WEST), direction=constants.WEST)

    def __move__(self, location, direction):
        return self.mob.Move(location=location, direction=direction)

# si.client = Client()
