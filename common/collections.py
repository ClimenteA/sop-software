from config import cfg
from enum import StrEnum
from .mongo_async import get_mongodb_connection, MongoAsync


mongodb_connection = get_mongodb_connection(cfg.get_mongo_uri(), cfg.MONGO_DATABASE)


class Col(StrEnum):
    ...


def get_collection(col: Col) -> MongoAsync:
    return MongoAsync(mongodb_connection, col)
