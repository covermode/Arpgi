# Keeping current game state    @LatypovIlya


from shared_lib.network import NetClient
from shared_lib.exts import Periodical
from shared_lib.shared_models import EntityModel


class ArpgiClient:
    def __init__(self, host, port):
        self.network = NetClient(host, port)
        self.name = self.network.name
        self.models = {owner_name: EntityModel(**model) for owner_name, model in
                       self.network.get("get_models").items()}
        self.run = True

        @self.network.route("update_models", method="SET")
        def update_models(sender_name, data):
            self.models = {owner_name: EntityModel(**model)
                           for owner_name, model in data.items()}
            return 0

        @self.network.route("update_model", method="SET")
        def update_model(sender_name, data):
            self.models[data["owner_name"]] = EntityModel(**data["model"])
            return 0

        @self.network.route("delete_model", method="SET")
        def delete_model(sender_name, data):
            self.models.pop(data["owner_name"])
            return 0

    def refresh_myself_model(self):
        self.models[self.name] = EntityModel(**self.network.get("get_model"))

    def move_at(self, delta: list):
        self.network.set("set_player_moving_target", data={
            "delta_pos": delta
        })
        self.models[self.name].delta_pos_x = delta[0]
        self.models[self.name].delta_pos_y = delta[1]
        # self.refresh_myself_model()

    def start(self):
        def update_models():
            for _, model in self.models.items():
                model.update_pos()

        self.model_updater = Periodical(update_models, 1 / 60)
        self.model_updater.start()

    def quit(self):
        self.network.kill()
        self.model_updater.stop()
        return 0
