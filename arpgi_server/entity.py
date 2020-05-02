class Entity:
    """Common game class of entity. Initializing with some basic params."""
    def __init__(self, rect, vel, d_pos_x=0, d_pos_y=0, alive=True):
        self._model = self.Model()

        self._model.rect = [rect[0], rect[1], rect[2], rect[3]]
        self._model.vel = vel
        self._model.d_pos = [d_pos_x, d_pos_y]
        self._model.alive = alive

    class Model:
        """Model of this class. Able to be sent to users"""
        def __init__(self):
            self.rect = [0, 0, 0, 0]
            self.vel = 0
            self.d_pos = [0, 0]
            self.alive = False

        def to_dict(self):
            ret = {}
            for field in self.__dict__:
                ret[field] = getattr(self, field)
            return ret

        def from_dict(self, val):
            for field in val:
                setattr(self, field, val[field])

    def set_moving_target(self, delta_pos):
        """Creates entity moving target. (relative position) Then entity required to move"""
        self._model.d_pos = [delta_pos[0], delta_pos[1]]

    def update_pos(self):
        if self._model.d_pos[0] == 0 and self._model.d_pos[1] == 0:
            return

        k = min(1, self._model.vel / (self._model.d_pos[0] ** 2 +
                                      self._model.d_pos[1] ** 2) ** 0.5)
        self._model.rect[0] += self._model.d_pos[0] * k
        self._model.rect[1] += self._model.d_pos[1] * k
        self._model.d_pos[0] *= (1 - k)
        self._model.d_pos[1] *= (1 - k)

    def get_model(self):
        return self._model.to_dict()
