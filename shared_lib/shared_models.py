# Common models for visuals.    @LatypovIlya


import time


class Rect:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.base = None

    def set_base(self, base):
        assert isinstance(base, SolidBase)
        base.add_solid(self)
        self.base = base

    def collide(self, other_solid):
        assert isinstance(other_solid, Rect)
        if self.x > other_solid.x + other_solid.w or other_solid.x > self.x + self.w:
            return False
        if self.y > other_solid.y + other_solid.h or other_solid.y > self.y + self.h:
            return False
        return True

    def __repr__(self):
        return f"<Rect> x:{self.x} y:{self.y} w:{self.w} h:{self.h}"


class SolidBase:
    def __init__(self):
        self._solids = []

    def add_solid(self, solid: Rect):
        self._solids.append(solid)

    def pop_solid(self, solid: Rect):
        self._solids.remove(solid)

    def get_solids(self):
        return self._solids.copy()

    def collide(self, rect: Rect):
        for r in self._solids:
            if r.collide(rect):
                return r
        return False


class EntityModel:
    """Common game class of movable object. Initializing with some basic params."""
    def __init__(self, name: str, x: float, y: float, w: float, h: float, vel: float,
                 delta_pos_x: float, delta_pos_y: float, motion_start_x: float,
                 motion_start_y: float, motion_start_time: float, alive: bool, _base=None):

        self.name = name
        self._rect = Rect(x, y, w, h)
        self.vel = vel
        self.delta_pos_x = delta_pos_x
        self.delta_pos_y = delta_pos_y

        self.motion_start_x = motion_start_x
        self.motion_start_y = motion_start_y
        self.motion_start_time = motion_start_time

        self.alive = alive
        self._base = _base

    @property
    def x(self):
        return self._rect.x

    @x.setter
    def x(self, val):
        self._rect.x = val

    @property
    def y(self):
        return self._rect.y

    @y.setter
    def y(self, val):
        self._rect.y = val

    @property
    def w(self):
        return self._rect.w

    @w.setter
    def w(self, val):
        self._rect.w = val

    @property
    def h(self):
        return self._rect.h

    @h.setter
    def h(self, val):
        self._rect.h = val

    def set_moving_target(self, delta_pos):
        """Creates entity moving target. (relative position) Then entity required to move"""
        self.motion_start_x = self.x
        self.motion_start_y = self.y
        self.motion_start_time = time.time()
        self.delta_pos_x, self.delta_pos_y = [delta_pos[0], delta_pos[1]]

    def update_pos(self):
        if self.x == self.motion_start_x + self.delta_pos_x and \
                self.y == self.motion_start_y + self.delta_pos_y:
            if self.delta_pos_x != 0 or self.delta_pos_y != 0:
                self.motion_start_x = self.x
                self.motion_start_y = self.y
                self.delta_pos_x = 0
                self.delta_pos_y = 0
            return

        assert isinstance(self._base, SolidBase)

        delta_time = time.time() - self.motion_start_time

        vel = delta_time * self.vel

        k = min(1.0, vel / (self.delta_pos_x ** 2 +
                            self.delta_pos_y ** 2) ** 0.5)
        prev_pos = (self.x, self.y)
        self.x = self.motion_start_x + self.delta_pos_x * k
        self.y = self.motion_start_y + self.delta_pos_y * k

        col = self._base.collide(self._rect)
        if col:
            print("Collided with:", col)
            self.x, self.y = prev_pos
            self.set_moving_target((0, 0))

    def get_model(self):
        return {
            'name': self.name,
            'x': self.x,
            'y': self.y,
            'w': self.w,
            'h': self.h,
            'vel': self.vel,
            'delta_pos_x': self.delta_pos_x,
            'delta_pos_y': self.delta_pos_y,
            'motion_start_x': self.motion_start_x,
            'motion_start_y': self.motion_start_y,
            'motion_start_time': self.motion_start_time,
            'alive': self.alive
        }

    def __str__(self):
        return str(self.get_model())

    def __repr__(self):
        return str(self)


class StaticModel:
    def __init__(self, name: str, x: float, y: float, w: float, h: float, _base=None):
        self.name = name
        self._rect = Rect(x, y, w, h)
        if _base is not None:
            self._rect.set_base(_base)

    def update_pos(self):
        return

    def get_model(self):
        return {
            'name': self.name,
            'x': self.x,
            'y': self.y,
            'w': self.w,
            'h': self.h
        }

    def set_solid_base(self, base: SolidBase):
        self._rect.set_base(base)

    @property
    def x(self):
        return self._rect.x

    @x.setter
    def x(self, val):
        self._rect.x = val

    @property
    def y(self):
        return self._rect.y

    @y.setter
    def y(self, val):
        self._rect.y = val

    @property
    def w(self):
        return self._rect.w

    @w.setter
    def w(self, val):
        self._rect.w = val

    @property
    def h(self):
        return self._rect.h

    @h.setter
    def h(self, val):
        self._rect.h = val
