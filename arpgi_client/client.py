# Keeping current game state    @LatypovIlya


from shared_lib.network import NetClient
from shared_lib.exts import Periodical
from shared_lib.models import EntityModel, StaticModel, SolidBase
from shared_lib.spell import search


class ArpgiClient:
    def __init__(self, host, port):
        self.network = NetClient(host, port)
        self.name = self.network.name
        self.room_info = self.network.get("get_room_info")
        self.map_size = self.room_info["room_size"]
        self.solid_base = SolidBase()
        self.statics = {name: StaticModel(**static, _base=self.solid_base)
                        for name, static in self.network.get("get_statics").items()}
        self.entities = {name: EntityModel(**entity, _base=self.solid_base)
                         for name, entity in self.network.get("get_entities").items()}
        self.current_spell = "FireBall"
        self.run = True

        # @self.network.route("update_models", method="SET")
        # def update_models(sender_name, data):
        #     self.models = {owner_name: EntityModel(**model)
        #                    for owner_name, model in data.items()}
        #     return 0

        @self.network.route("update_entities", method="SET")
        def update_entities(sender_name, data):
            self.entities = {name: EntityModel(**entity, _base=self.solid_base)
                             for name, entity in data.items()}
            return 0

        # @self.network.route("update_model", method="SET")
        # def update_model(sender_name, data):
        #     self.models[data["owner_name"]] = EntityModel(**data["model"])
        #     return 0

        @self.network.route("update_entity", method="SET")
        def update_entity(sender_name, data):
            self.entities[data["owner_name"]] = EntityModel(**data["model"],
                                                            _base=self.solid_base)
            return 0

        # @self.network.route("delete_model", method="SET")
        # def delete_model(sender_name, data):
        #     self.models.pop(data["owner_name"])
        #     return 0

        @self.network.route("delete_entity", method="SET")
        def delete_entity(sender_name, data):
            self.entities.pop(data["owner_name"])
            return 0

        @self.network.route("set_used_spell", method="SET")
        def set_used_spell(sender_name, data):
            self.use_spell(data["spell_name"], data["owner_name"],
                           data["delta_pos"])
            return 0

    def refresh_myself_model(self):
        self.entities[self.name] = EntityModel(**self.network.get("get_player"),
                                               _base=self.solid_base)

    def move_at(self, delta: list):
        me = self.entities[self.name]
        if 0 <= me.x + delta[0] and me.x + me.w + delta[0] <= self.map_size[0] and \
                0 <= me.y + delta[1] and me.y + me.h + delta[1] <= self.map_size[1]:
            self.network.set("set_player_moving_target", data={
                "delta_pos": delta
            })
            me.set_moving_target(delta)
        else:
            pass
        # self.refresh_myself_model()

    def use_spell(self, name, by: EntityModel, delta_pos):
        projectiles = search(name).cast((by.x + by.w // 2, by.y + by.h // 2),
                                        delta_pos, self.solid_base)

        for prj in projectiles:
            self.entities[prj.name] = prj

    def shoot(self, delta: list):
        self.use_spell(self.current_spell, self.entities[self.name], delta)

        self.network.set("use_spell", data={
            "spell_name": self.current_spell,
            "delta_pos": delta
        })

    def start(self):
        def update_models():
            dead = []
            for _, model in self.entities.items():
                if not model.alive:
                    dead.append(_)
                    continue
                model.update_pos()
            for _ in dead:
                self.entities.pop(_)

        self.model_updater = Periodical(update_models, 1 / 60)
        self.model_updater.start()

    def quit(self):
        self.network.kill()
        self.model_updater.stop()
        return 0
