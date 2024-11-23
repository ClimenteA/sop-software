from pymongo import MongoClient
from pymongo.cursor import Cursor
from pymongo.database import Database
from pymongo.collection import Collection


def get_mongodb_connection(mongo_uri: str, db: str):
    mongo_connection = MongoClient(mongo_uri)[db]
    mongo_connection.list_collection_names()
    return mongo_connection


def get_limit_skip_from_page(page: int, items_per_page: int):
    try:
        page = abs(int(page))
        if page <= 0:
            page = 1
    except Exception:
        page = 1

    limit = items_per_page
    skip = 0 if page == 1 else (page - 1) * items_per_page

    return limit, skip


class MongoAsync:
    def __init__(self, db_connection: Database, collection_name: str):
        self.db_connection = db_connection
        self.collection_name = collection_name
        self.col: Collection = db_connection[collection_name]

    def _pop_id(self, data: dict):
        data.pop("_id", None)
        return data

    def _parse_one(self, data: dict):
        return self._pop_id(data or {})

    def _parse(self, cursor: Cursor):
        return [self._pop_id(doc) for doc in cursor]

    async def aggregate(self, query: list[dict]) -> list[dict]:
        cursor = self.col.aggregate(pipeline=query, allowDiskUse=True)
        return self._parse(cursor)

    async def find_one(self, filters: dict, projection: dict = None) -> dict:
        data = self.col.find_one(filters, projection=projection)
        return self._parse_one(data)

    async def find_many(
        self,
        filters: dict,
        page: int = None,
        items_per_page: int = 20,
        limit: int = 0,
        skip: int = 0,
        sort: list[tuple[str, int]] = None,
        projection: dict = None,
    ) -> list[dict]:
        if projection is None:
            projection = {"_id": 0}

        if page is not None:
            limit, skip = get_limit_skip_from_page(page, items_per_page)

        cursor = self.col.find(
            filter=filters,
            skip=skip,
            limit=limit,
            sort=sort,
            projection=projection,
        )
        return self._parse(cursor)

    async def distinct(
        self,
        field: str,
        filters: dict = None,
    ) -> list[str]:
        data = self.col.distinct(key=field, filter=filters)
        return data

    async def count(self, filters: dict = None) -> int:
        if filters is None:
            filters = {}
        return self.col.count_documents(filter=filters)

    async def insert_one(self, data: dict) -> dict:
        self.col.insert_one(data)
        return data

    async def insert_many(
        self,
        data: list[dict],
    ) -> list[dict]:
        self.col.insert_many(data)
        return self._parse(data)

    async def update_one(
        self,
        filters: dict,
        data: dict,
        upsert: bool = False,
    ) -> dict:
        data = self.col.find_one_and_update(
            filter=filters,
            update=data
            if any([k for k in data.keys() if k.startswith("$")])
            else {"$set": data},
            upsert=upsert,
            return_document=True,
        )
        return self._parse_one(data)

    async def update_many(
        self,
        filters: dict,
        data: list[dict],
        upsert: bool = False,
    ) -> int:
        return self.col.update_many(
            filter=filters,
            update=data
            if any([k for k in data.keys() if k.startswith("$")])
            else {"$set": data},
            upsert=upsert,
        ).matched_count

    async def delete_one(self, filters: dict) -> int:
        return self.col.delete_one(filter=filters).deleted_count

    async def delete_many(self, filters: dict) -> int:
        return self.col.delete_many(filter=filters).deleted_count
