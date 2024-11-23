from common.logger import log
import apps.sop.models.collections as c


async def get_user_sops(user_id: str):
    try:
        sops = await c.SopsCol.find_many(
            filters={"writers": {"$in": [user_id]}},
        )
        if not sops:
            return []

        for sop in sops:
            writers = await c.UsersCol.find_many(
                {"user_id": {"$in": sop["writers"]}},
                projection={"_id": 0, "name": 1},
            )
            sop["writers"] = [w["name"] for w in writers]

        return sops
    except Exception as err:
        log.exception(err)

    return []
