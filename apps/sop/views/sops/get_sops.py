import pymongo
import Levenshtein
from common.logger import log
from datetime import datetime, timedelta
import apps.sop.models.collections as c
from apps.sop.text_utils import make_slug_from_text
from apps.sop.models.sop import SopSearchOnDbModel


async def save_search(search: str, tenant_id: str):
    if not all([search, tenant_id]):
        return

    if len(search) >= 3:
        try:
            searches_nbr = await c.SopSearchesCol.count({"tenant_id": tenant_id})
            if searches_nbr > 500_000:
                oldest_date = (datetime.utcnow() - timedelta(days=90)).isoformat()
                await c.SopSearchesCol.delete_many(
                    {"tenant_id": tenant_id, "searched_at": oldest_date}
                )

            await c.SopSearchesCol.insert_one(
                SopSearchOnDbModel(search=search, tenant_id=tenant_id).model_dump()
            )
        except pymongo.errors.DuplicateKeyError:
            return


async def get_sops(page: int, search: str, topic: str, tenant_id: str):
    try:
        query = {}

        if tenant_id:
            query.update({"tenant_id": tenant_id})
        else:
            query.update({"public": True})

        if topic:
            query.update({"topics": {"$in": [topic]}})

        if search:
            slug = make_slug_from_text(search)
            sop_from_slug = await c.SopsCol.find_one({"sop_id": slug})
            if sop_from_slug:
                return sop_from_slug

            query = {
                "$or": [
                    {"title": {"$regex": word, "$options": "i"}},
                    {"purpose": {"$regex": word, "$options": "i"}},
                    {"application": {"$regex": word, "$options": "i"}},
                    {"content": {"$regex": word, "$options": "i"}},
                ]
                for word in slug.split("-")
            }

        sops = await c.SopsCol.find_many(
            query,
            page=page,
            sort=[("views", pymongo.DESCENDING), ("rating", pymongo.DESCENDING)],
        )
        if not sops:
            await save_search(search, tenant_id)
            return []

        companies = {}
        for sop in sops:
            if sop["tenant_id"] not in companies:
                companies[sop["tenant_id"]] = await c.UsersCol.find_one(
                    {"tenant_id": sop["tenant_id"]}
                )

            sop["company"] = companies[sop["tenant_id"]]["company"]

            writers = await c.UsersCol.find_many(
                {"user_id": {"$in": sop["writers"]}},
                projection={"_id": 0, "name": 1},
            )
            sop["writer_names"] = [w["name"] for w in writers]

        if search:
            for d in sops:
                d["score"] = sum(
                    [
                        Levenshtein.distance(search, v)
                        for k, v in d.items()
                        if k in ["title", "purpose", "application", "content"]
                    ]
                )

            sops = sorted(
                sops,
                key=lambda x: (
                    x["score"],
                    x.get("title", ""),
                    x.get("purpose", ""),
                    x.get("application", ""),
                    x.get("content", ""),
                ),
            )

        return sops
    except Exception as err:
        log.exception(err)

    return []
