from shared_lib.models import EntityModel
import random


def search(name):
    its = globals()[name]
    if not issubclass(its, Spell):
        raise ValueError("Can search only spells")
    return its


class Spell:
    class Projectile(EntityModel):
        pass

    @classmethod
    def cast(cls, from_pos, delta_pos, solid_base=None):
        raise NotImplementedError("Sry not implemented")


class FireBall(Spell):
    class FireBallProjectile(Spell.Projectile):
        def update_pos(self):
            super(FireBall.FireBallProjectile, self).update_pos()
            if (self.delta_pos_x == 0) and (self.delta_pos_y == 0):
                self.alive = False

    @classmethod
    def cast(cls, from_pos, delta_pos, solid_base=None):
        projectile = FireBall.FireBallProjectile.generate_entity(
            name=f"{cls.__name__}:<Projectile {random.randint(100000, 999999)}>",
            rect=(*from_pos, 10, 10), vel=200, delta=delta_pos, base=solid_base
        )
        return [projectile]
