import apps.sop.models.collections as c
from common.logger import log


async def get_user_by_id(user_id: str):
    try:
        user = await c.UsersCol.find_one(filters={"user_id": user_id})
        if user:
            return user
    except Exception as err:
        log.exception(err)
    return None
