# Models package. @LatypovIlya
"""This package contains off-line models of entities, this models is being used for
processes on local client, to save bandwidth and send to server mostly only user actions"""


class EntityModel:
    """Model of Entity, described in 'entity.py' in server. Stores data for computing in client
    machines"""
    def __init__(self, model: dict):
        """Takes json-like dict with all fields of model stored in
        :param model: the json-like dict with 'rect', 'vel', 'd_pos', 'alive' fields in
        """
        self.rect = model["rect"]
        self.vel = model["vel"]
        self.d_pos = model["d_pos"]
        self.alive = model["alive"]

    def update_pos(self):
        """Simple math function of calculating current move by velocity
        (in pixels per tick), and vector, defined in d_pos as x, y"""
        if self.d_pos[0] == 0 and self.d_pos[1] == 0:
            return

        k = min(1, self.vel / (self.d_pos[0] ** 2 +
                               self.d_pos[1] ** 2) ** 0.5)
        self.rect[0] += self.d_pos[0] * k
        self.rect[1] += self.d_pos[1] * k
        self.d_pos[0] *= (1 - k)
        self.d_pos[1] *= (1 - k)
