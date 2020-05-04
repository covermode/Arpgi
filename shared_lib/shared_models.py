# Common models for visuals.    @LatypovIlya


class EntityModel:
    """Common game class of movable object. Initializing with some basic params."""
    def __init__(self, x: float, y: float, w: float, h: float, vel: float,
                 delta_pos_x: float, delta_pos_y: float, alive: bool):

        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.vel = vel
        self.delta_pos_x = delta_pos_x
        self.delta_pos_y = delta_pos_y
        self.alive = alive

    def set_moving_target(self, delta_pos):
        """Creates entity moving target. (relative position) Then entity required to move"""
        self.delta_pos_x, self.delta_pos_y = [delta_pos[0], delta_pos[1]]

    def update_pos(self):
        if self.delta_pos_x == 0 and self.delta_pos_y == 0:
            return

        k = min(1.0, self.vel / (self.delta_pos_x ** 2 +
                                 self.delta_pos_y ** 2) ** 0.5)
        self.x += self.delta_pos_x * k
        self.y += self.delta_pos_y * k
        self.delta_pos_x *= (1 - k)
        self.delta_pos_y *= (1 - k)

    def get_model(self):
        return {
            'x': self.x,
            'y': self.y,
            'w': self.w,
            'h': self.h,
            'vel': self.vel,
            'delta_pos_x': self.delta_pos_x,
            'delta_pos_y': self.delta_pos_y,
            'alive': self.alive
        }


class StaticModel:
    def __init__(self, x: float, y: float, w: float, h: float):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def get_model(self):
        return {
            'x': self.x,
            'y': self.y,
            'w': self.w,
            'h': self.h
        }
