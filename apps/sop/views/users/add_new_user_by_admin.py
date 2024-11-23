from apps.sop.models.user import UserOnInviteModel, UserOnInviteInDbModel, Role
import apps.sop.models.collections as c
from common.responses import CustomResponse, State
from common.logger import log
from config import cfg


BASE_INVITE_URL = f"https://sop.softgata.{'localhost' if cfg.DEBUG else 'com'}/sop/register?invite_token="


async def add_new_user_by_admin(tenant_id: str, user: UserOnInviteModel):
    try:
        user = UserOnInviteInDbModel(**user.model_dump(), tenant_id=tenant_id)

        updated = await c.InvitedUsersCol.update_one(
            filters={"email": user.email, "tenant_id": tenant_id},
            data=user.model_dump(),
            upsert=True,
        )
        if updated:
            URL = BASE_INVITE_URL + user.token
            return CustomResponse(
                status=State.SUCCESS,
                status_code=200,
                content={
                    "email": user.email,
                    "role": user.role.capitalize()
                    if user.role != Role.SME
                    else user.role.upper(),
                    "url": URL,
                },
            )
    except Exception as err:
        log.exception(err)

    return CustomResponse(
        status=State.FAILED, status_code=500, content="Please try again"
    )
