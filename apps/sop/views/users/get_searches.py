from apps.sop.models.collections import SopSearchesCol
from common.logger import log


async def get_searches(tenant_id: str):
    try:
        results = await SopSearchesCol.find_many(
            {"tenant_id": tenant_id}, projection={"search": 1, "_id": 0}
        )
        if results:
            return results
    except Exception as err:
        log.exception(err)
    return None
