from .icon import IconDescriptor
from .icon_state import IconStateDescriptor
from .world_map import WorldMap


class MappableMeta(type):
    _icon = None
    _icon_state = None
    icon = IconDescriptor()
    icon_state = IconStateDescriptor()

    def __new__(mcs, name, bases, dct):
        icon = dct.get('icon')
        if isinstance(icon, str):
            dct['icon'] = IconDescriptor()

        icon_state = dct.get('icon_state')
        if isinstance(icon_state, str):
            dct['icon_state'] = IconStateDescriptor()

        cls = super(MappableMeta, mcs).__new__(mcs, name, bases, dct)
        if isinstance(icon, str):
            cls.icon = icon
        if isinstance(icon_state, str):
            cls.icon_state = icon_state

        return cls

    def __init__(cls, name, bases, dct):
        super(MappableMeta, cls).__init__(name, bases, dct)
        WorldMap.types.add(cls)

