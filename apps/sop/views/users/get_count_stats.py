import apps.sop.models.collections as c
from apps.sop.models.user import Role
from common.logger import log


async def get_count_stats(tenant_id: str):
    try:
        total_views = 0
        pipeline = [
            {"$match": {"tenant_id": tenant_id}},
            {"$group": {"_id": None, "total_views": {"$sum": "$views"}}},
        ]
        result = await c.SopsCol.aggregate(pipeline)
        if result:
            total_views = result[0]["total_views"]

        total_sops = await c.SopsCol.count({"tenant_id": tenant_id})
        total_readers = await c.UsersCol.count(
            {"tenant_id": tenant_id, "role": Role.READER}
        )
        total_writers = await c.UsersCol.count(
            {"tenant_id": tenant_id, "role": {"$in": [Role.SME, Role.ADMIN]}}
        )

        return {
            "total_views": total_views,
            "total_sops": total_sops,
            "total_readers": total_readers,
            "total_writers": total_writers,
        }

    except Exception as err:
        log.exception(err)

    return {
        "total_views": 0,
        "total_sops": 0,
        "total_readers": 0,
        "total_writers": 0,
    }
