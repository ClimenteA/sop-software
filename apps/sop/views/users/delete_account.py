from apps.sop.models.collections import UsersCol
from common.logger import log
from common.responses import CustomResponse, State


async def delete_account(user_id: str):
    try:
        query = {"user_id": user_id, "tenant_id": {"$ne": user_id}}
        await UsersCol.delete_one(query)
        return CustomResponse("User was deleted")
    except Exception as err:
        log.exception(err)
    return CustomResponse(
        content="Please try again",
        status=State.FAILED,
        status_code=500,
    )
