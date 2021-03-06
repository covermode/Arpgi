# Game state updater


from shared_lib.models import EntityModel, StaticModel, SolidBase
from shared_lib.spell import search
import data.model_refuser as model_refuser


class Map:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.spawn_point_pos = (self.width // 2, self.height // 2)


class Room:
    def __init__(self, map_size):
        import os
        self.players = {}
        self.entities = {}
        self.statics = {}
        self.solid_base = SolidBase()
        self.map = Map(map_size[0], map_size[1])
        model_refuser.init(os.path.join(*os.path.split(__file__)[:-1],
                                        "data", "db", "data.sqlite"))

        for item in model_refuser.refuse_static():
            self.statics[item.name + str(item.id)] = StaticModel(
                name=item.name, x=item.x, y=item.y, w=item.w, h=item.h, _base=self.solid_base
            )

        for item in model_refuser.refuse_entity():
            self.statics[item.name + str(item.id)] = EntityModel(
                name=item.name,
                x=item.x, y=item.y, w=item.w, h=item.h, vel=item.vel,
                delta_pos_x=0, delta_pos_y=0, motion_start_x=item.x,
                motion_start_y=item.y, motion_start_time=0, alive=True,
                _base=self.solid_base
            )
        print("ok")

    def add_player(self, name, player_data) -> EntityModel:
        self.players[name] = EntityModel(**player_data, _base=self.solid_base)
        self.entities[name] = self.players[name]
        return self.players[name]

    def get_static(self, name) -> StaticModel:
        return self.statics[name]

    def get_entity(self, name) -> EntityModel:
        return self.entities[name]

    def get_static_models(self):
        return {
            name: item.get_model() for name, item in self.statics.items()
        }

    def get_entity_models(self):
        return {
            name: item.get_model() for name, item in self.entities.items()
        }

    def get_models(self):
        return {
            'static': self.get_static_models(),
            'entity': self.get_entity_models()
        }

    def use_spell(self, spell_name, owner_name, delta_pos):
        owner = self.player(owner_name)
        projectiles = search(spell_name).cast((owner.x, owner.y), delta_pos, self.solid_base)
        for prj in projectiles:
            self.entities[prj.name] = prj
        return projectiles

    def pop_player(self, name) -> EntityModel:
        player = self.players[name]
        self.entities.pop(name)
        self.players.pop(name)
        return player

    def player(self, owner_name) -> EntityModel:
        ret = self.players[owner_name]
        assert isinstance(ret, EntityModel)
        return ret

    def update(self):
        dead = []
        for name, entity in self.entities.items():
            assert isinstance(entity, EntityModel)
            if entity.alive:
                entity.update_pos()
            else:
                dead.append(name)
        for name in dead:
            self.entities.pop(name)

    @property
    def spawn_point(self):
        return self.map.spawn_point_pos

    @property
    def map_size(self):
        return self.map.width, self.map.height
