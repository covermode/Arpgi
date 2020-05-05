from .db_session import global_init, create_session
from .__all_models import StaticInitializer, EntityInitializer


def refuse_static():
    session = create_session()
    return list(session.query(StaticInitializer).all())


def refuse_entity():
    session = create_session()
    return list(session.query(EntityInitializer).all())


def init(path_to_db):
    global_init(path_to_db)
