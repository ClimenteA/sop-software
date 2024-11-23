from apps.sop.models.collections import UsersCol
from apps.sop.models.user import UserOnAvatarModel
from common.logger import log
from common.responses import CustomResponse, State


async def update_avatar(user_id: str, avatar: UserOnAvatarModel):
    try:
        updated = await UsersCol.update_one(
            {"user_id": user_id}, data=avatar.model_dump()
        )
        if updated:
            return CustomResponse(content="Picture uploaded")
    except Exception as err:
        log.exception(err)
    return CustomResponse(
        content="Please try again", status=State.FAILED, status_code=500
    )
