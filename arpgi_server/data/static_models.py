import sqlalchemy
from .db_session import SqlAlchemyBase


class StaticInitializer(SqlAlchemyBase):
    __tablename__ = "static"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    x = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    y = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    w = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    h = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)

    def __repr__(self):
        return f"<StaticInitializer> rect:[{self.x}, {self.y}, {self.width}, {self.height}]"
