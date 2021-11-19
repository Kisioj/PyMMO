import time
import logging
import types
from collections import namedtuple

from . import constants
from . import singletons as si
"""
Docstring convention: http://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html
"""


def get_step(ref, direction: int, dist: int = 1):
    """Calculate the position of `dist` steps from ref in the given direction.

    Args:
        ref (Atom): Starting point or object.
        direction (int): One of NORTH, SOUTH, EAST, WEST,
                         NORTHEAST, NORTHWEST, SOUTHEAST, SOUTHWEST.
        dist (int): Number of steps to take. 1 by default.

    Returns:
        Location: The location of the new position
    """
    x, y, z = ref.x, ref.y, ref.z
    if direction & constants.NORTH:
        y += dist
    if direction & constants.SOUTH:
        y -= dist
    if direction & constants.WEST:
        x -= dist
    if direction & constants.EAST:
        x += dist

    from . import base_types
    return base_types.Location(x, y, z)


def locate(*args, **kwargs):
    from . import base_types
    """
    Format:
        locate(prototype, container=world)
        locate(x, y, z)
        locate(tag)
        locate(text_ref)

    Args:
        prototype: An object prototype. (Must be mappable.)
        container: An optional container object. (The default is world.)
        x, y, z: A set of numerical coordinates.
        tag: The value of an object's tag variable (must be unique).
        text_ref: An embedded object reference created by the \ref text macro.

    Returns:
        An object of the specified type or the turf at the given coordinates.
        If a text string is given in place of an object type, the object with
        the same tag is found. If a container is given, only objects directly
        within that object are searched.
    """
    def locate_by_type(prototype: base_types.MappableMeta):
        pass

    def locate_by_coords(x: int, y: int, z: int = 1):
        return base_types.Location(x, y, z)

    def locate_by_tag(tag: str):
        pass

    def locate_by_text_ref(text_ref: str):
        pass

    if args:
        first_arg = args[0]
    elif kwargs:
        first_arg = next(iter(kwargs.values()))
    else:
        raise TypeError('No arguments given')

    if isinstance(first_arg, int):
        locate_func = locate_by_coords
    elif isinstance(first_arg, str):
        locate_func = locate_by_tag
    elif issubclass(first_arg, base_types.Atom):
        locate_func = locate_by_type
    else:
        raise TypeError('Incorrect arguments')

    return locate_func(*args, **kwargs)


def sleepy(func):
    def outer(self, *args, **kwargs):
        def inner():
            try:
                seconds = next(result)
                spawn(inner, seconds)
            except StopIteration:
                logging.info('STOP')
                pass
        result = func(self, *args, **kwargs)
        if isinstance(result, types.GeneratorType):
            inner()
        return None  # return result would suck
    return outer


def sleep(delay: float):
    """Pause the current proc (and its callers) for a specified amount of
    time. If no delay is specified, it will be scheduled to resume as soon
    as other immediately pending events are processed.

    Note that sleeping in some procedures results in the return value being
    lost. For example, if you sleep inside Enter() or Exit(), it will be as
    if you returned immediately where you started sleeping.

    Also be aware, that a sleeping procedure whose src object gets deleted
    will automatically terminate when execution returns to it. This is to
    protect you against trying to access properties or procedures of a
    deleted (and therefore null) object. If you do not want the procedure
    to be terminated, you should set src to null.

    One common use of sleep is to create what is known as a ticker. That
    is an infinite loop that performs some periodic operation.

    Args:
        delay: The amount of time to sleep, in 1/10 seconds.
    """
    logging.info('sleep', delay*10, 'seconds')
    return delay/10.0


def spawn(function, delay: float = 0):
    """Run function after a delay. `function` may be a method or a function.
    If delay is negative, the spawned code is executed before continuing in
    the main code. If it is zero, the spawned code is scheduled to happen
    right after other existing events that are immediately pending.

    Args:
        delay: The amount of time (in 1/10 seconds) before Statement is executed.
    """
    si.functions_queue.append([time.time() + delay/10.0, function])


def get_by_type(loc, types):
    return (atom for atom in loc if isinstance(atom, types))


def get_dist(source, target):
    return abs(source.x - target.x) + abs(source.y - target.y)


def delete(atom):
    atom.__remove__()


def step(ref, direction: int):
    ref.Move(location=get_step(ref, direction), direction=direction)


class WalkParams:
    def __init__(self, direction, lag, ticks_left):
        self.direction = direction
        self.lag = lag
        self.ticks_left = ticks_left


def walk(ref, direction, lag=0):
    if direction:
        si.walking[ref] = WalkParams(direction=direction, lag=lag, ticks_left=lag)
    elif ref in si.walking:
        del si.walking[ref]
