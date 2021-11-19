from PyBYOND import singletons as si
from PyBYOND import base_types


class World:
    _view_width = None
    _view_height = None

    def __init__(self):
        self.mob = None # base_types.Mob()  # Mob
        self.icon_size = 32  #  TODO mozliwosc dodania "32x32"
        self.view = 5
        self.maps = []  # moze byc wiecej map
        self.map = None

    @property
    def view(self):
        """
        This is the default map viewport range. The default value of 5
        produces an 11x11 viewport. A value of -1 turns off the map display
        altogether. The client may automatically scale down icons in order to
        conveniently fit the map on the player's screen.

        For non-square views, you can assign this to a text string of the
        form "WIDTHxHEIGHT". For example, "11x11" is equivalent to a view
        depth of 5, but you could make it wider like this: "13x11".

        This setting also affects the default range of the view(), oview(),
        brange(), and orange() procedures.

        If the entire map is small enough to fit on one screen (arbitrarily
        defined to be 21x21 or less), the default view is automatically
        adjusted to fit the map. In this case, client.lazy_eye is also
        automatically turned on by default, since you probably don't want
        the map to scroll around.

        Default value:
            5
        Possible values:
            -1 to 34 or "WIDTHxHEIGHT"
        """
        if self._view_width == self._view_height and self._view_width % 2:
            return (self._view_width - 1) // 2
        else:
            return "{}x{}".format(self._view_width, self._view_height)

    @view.setter
    def view(self, value):
        if isinstance(value, str):
            self._view_width, self._view_height = map(int, value.split('x'))
        elif isinstance(value, int):
            view = value * 2 + 1
            self._view_width, self._view_height = view, view
        else:
            raise TypeError("Incorrent view argument type")

# si.world = World()
