from datetime import datetime
import apps.sop.models.collections as c
from common.logger import log


async def get_sop_by_id(sop_id: str, user_id: str, count_view: bool = False):
    try:
        sop_query = {"sop_id": sop_id}

        if user_id is None:
            sop_query.update({"public": True})

        sop = await c.SopsCol.find_one(sop_query)

        if sop:
            if count_view:
                query = {"sop_id": sop_id}
                if user_id:
                    query.update({"writers": {"$nin": [user_id]}})

                await c.SopsCol.update_one(
                    filters=query,
                    data={
                        "$set": {"last_viewed_on": datetime.utcnow().isoformat()},
                        "$inc": {"views": 1},
                    },
                )

            writers = await c.UsersCol.find_many(
                {"user_id": {"$in": sop["writers"]}},
                projection={"_id": 0, "name": 1},
            )
            sop["writers"] = [w["name"] for w in writers]

            return sop
    except Exception as err:
        log.exception(err)

    return None
