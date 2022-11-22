from pymmo import singletons as si


class Location:
    def __init__(self, x, y, z=1):
        from pymmo.base_types.mappable.turf import Turf  # FIXME, tutaj przez circual import
        from pymmo.base_types.mappable.area import Area
        self.x, self.y, self.z = x, y, z
        self.cell = si.world.map.fields[y][x]
        self.turfs = []
        self.areas = []
        self.areas_classes = []
        for atom in self.cell:
            if isinstance(atom, Turf):
                self.turfs.append(atom)
            elif isinstance(atom, Area):
                self.areas.append(atom)
                self.areas_classes.append(atom.__class__)

    def __repr__(self):
        from pymmo.base_types.mappable.turf import Turf  #FIXME, tutaj przez circual import
        return '{} ({}, {})'.format([
            atom for atom
            in self.cell
            if isinstance(atom, Turf)
        ][0].__class__.__name__, self.x, self.y)

    def __iter__(self):
        """
        :return: iterator to copy of self.cell
        so it is safe to remove elements
        from map while iterating
        """
        return iter(list(self.cell))

    def __eq__(self, other):
        return (self.x, self.y) == (other.x, other.y)

    def Exit(self, movable, new_location):
        for turf in self.turfs:
            if not turf.Exit(movable, new_location):
                return False

        for area in self.areas:
            if area.__class__ not in new_location.areas_classes:
                # print 'area.__class__ ({}) VS new_location.areas_classes ({})'.format(area.__class__, new_location.areas_classes)
                if not area.Exit(movable, new_location):
                    return False

        return True

    def Enter(self, movable, old_location):
        result = True
        for turf in self.turfs:
            if not turf.Enter(movable, old_location):
                result = False

        for area in self.areas:
            if area.__class__ not in old_location.areas_classes:
                # print 'area.__class__ ({}) VS old_location.areas_classes ({})'.format(area.__class__, old_location.areas_classes)
                if not area.Enter(movable, old_location):
                    result = False

        return result

    def Exited(self, movable, new_location):
        for turf in self.turfs:
            turf.Exited(movable, new_location)

        for area in self.areas:
            if area.__class__ not in new_location.areas_classes:
                area.Exited(movable, new_location)


    def Entered(self, movable, old_location):
        for turf in self.turfs:
            turf.Entered(movable, old_location)

        for area in self.areas:
            if area.__class__ not in old_location.areas_classes:
                area.Entered(movable, old_location)
