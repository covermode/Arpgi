# Keeping current game state    @LatypovIlya


from shared_lib.network import NetClient
from shared_lib.exts import Periodical
from shared_lib.shared_models import EntityModel, StaticModel


class ArpgiClient:
    def __init__(self, host, port):
        self.network = NetClient(host, port)
        self.name = self.network.name
        self.room_info = self.network.get("get_room_info")
        self.map_size = self.room_info["room_size"]
        self.statics = {name: StaticModel(**static)
                        for name, static in self.network.get("get_statics").items()}
        self.entities = {name: EntityModel(**entity)
                         for name, entity in self.network.get("get_entities").items()}
        self.run = True

        # @self.network.route("update_models", method="SET")
        # def update_models(sender_name, data):
        #     self.models = {owner_name: EntityModel(**model)
        #                    for owner_name, model in data.items()}
        #     return 0

        @self.network.route("update_entities", method="SET")
        def update_entities(sender_name, data):
            self.entities = {name: EntityModel(**entity)
                             for name, entity in data.items()}
            return 0

        # @self.network.route("update_model", method="SET")
        # def update_model(sender_name, data):
        #     self.models[data["owner_name"]] = EntityModel(**data["model"])
        #     return 0

        @self.network.route("update_entity", method="SET")
        def update_entity(sender_name, data):
            self.entities[data["owner_name"]] = EntityModel(**data["model"])
            return 0

        # @self.network.route("delete_model", method="SET")
        # def delete_model(sender_name, data):
        #     self.models.pop(data["owner_name"])
        #     return 0

        @self.network.route("delete_entity", method="SET")
        def delete_entity(sender_name, data):
            self.entities.pop(data["owner_name"])
            return 0

    def refresh_myself_model(self):
        self.entities[self.name] = EntityModel(**self.network.get("get_player"))

    def move_at(self, delta: list):
        if 0 <= self.entities[self.name].x + delta[0] <= self.map_size[0] and \
                0 <= self.entities[self.name].y + delta[1] <= self.map_size[1]:
            self.network.set("set_player_moving_target", data={
                "delta_pos": delta
            })
            self.entities[self.name].set_moving_target(delta)
        else:
            pass
        # self.refresh_myself_model()

    def start(self):
        def update_models():
            for _, model in self.entities.items():
                model.update_pos()

        self.model_updater = Periodical(update_models, 1 / 60)
        self.model_updater.start()

    def quit(self):
        self.network.kill()
        self.model_updater.stop()
        return 0
