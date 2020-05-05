# Common models for visuals.    @LatypovIlya


import time


class EntityModel:
    """Common game class of movable object. Initializing with some basic params."""
    def __init__(self, name: str, x: float, y: float, w: float, h: float, vel: float,
                 delta_pos_x: float, delta_pos_y: float, motion_start_x: float,
                 motion_start_y: float, motion_start_time: float, alive: bool):

        self.name = name
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.vel = vel
        self.delta_pos_x = delta_pos_x
        self.delta_pos_y = delta_pos_y

        self.motion_start_x = motion_start_x
        self.motion_start_y = motion_start_y
        self.motion_start_time = motion_start_time

        self.alive = alive

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

        delta_time = time.time() - self.motion_start_time

        vel = delta_time * self.vel

        k = min(1.0, vel / (self.delta_pos_x ** 2 +
                            self.delta_pos_y ** 2) ** 0.5)
        self.x = self.motion_start_x + self.delta_pos_x * k
        self.y = self.motion_start_y + self.delta_pos_y * k

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
    def __init__(self, name: str, x: float, y: float, w: float, h: float):
        self.name = name
        self.x = x
        self.y = y
        self.w = w
        self.h = h

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
