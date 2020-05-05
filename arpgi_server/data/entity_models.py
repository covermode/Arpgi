import sqlalchemy
from .db_session import SqlAlchemyBase


class EntityInitializer(SqlAlchemyBase):
    __tablename__ = "entity"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    x = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    y = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    w = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    h = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    vel = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    alive = sqlalchemy.Column(sqlalchemy.Boolean, default=True)

    def __repr__(self):
        return f"<EntityInitializer {self.name}{self.id}> rect:[{self.x}, {self.y}, " \
               f"{self.width}, {self.height}] vel: {self.vel} alive: {self.alive}"
