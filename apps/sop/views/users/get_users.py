import apps.sop.models.collections as c
from common.logger import log
from common.responses import CustomResponse, State


async def get_users(page: int, search: str):
    try:
        query = {}
        if search is not None:
            query = {
                "$or": [
                    {"name": {"$regex": search, "$options": "i"}},
                    {"email": {"$regex": search, "$options": "i"}},
                ]
            }

        users = await c.UsersCol.find_many(filters=query, page=page)

        return users

    except Exception as err:
        log.exception(err)

    return CustomResponse(
        content=[],
        status=State.FAILED,
        status_code=400,
    )
