from apps.sop.models.collections import SopsCol
from apps.sop.models.sop import SopRatingOnPostModel
from common.logger import log


async def rate_sop(user_id: str, rating: SopRatingOnPostModel):
    try:
        sop_query = {"sop_id": rating.sop_id}

        if user_id is None:
            sop_query.update({"public": True})

        await SopsCol.update_one(
            filters=sop_query,
            data={"$inc": {"rating": 1 if rating.rating else -1}},
        )
    except Exception as err:
        log.exception(err)
