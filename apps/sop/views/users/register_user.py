from config import cfg
from datetime import datetime, timedelta, timezone
from apps.sop.models.user import UserOnDbModel, UserOnRegisterModel, Role
from common.responses import CustomResponse, State
from common.logger import log
from apps.sop.models.collections import UsersCol, InvitedUsersCol
from .get_info_from_invite_token import get_info_from_invite_token


async def register_user(user: UserOnRegisterModel, invite_token: str = None):
    try:
        already_exists = await UsersCol.count({"email": user.email})
        if already_exists:
            return CustomResponse(
                content="Email is already registered",
                status=State.FAILED,
                status_code=400,
            )

        role = Role.ADMIN
        tenant_id = None
        if invite_token is not None:
            company, invited_email = await get_info_from_invite_token(invite_token)
            if user.company != company or user.email != invited_email:
                await InvitedUsersCol.delete_one({"token": invite_token})
                return CustomResponse(
                    content="Invalid values for this invite token. Token invalidated.",
                    status=State.FAILED,
                    status_code=400,
                )

            date = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            invited_user = await InvitedUsersCol.find_one(
                {"token": invite_token, "invited_on": {"$gte": date}}
            )
            if invited_user:
                role = invited_user["role"]
                tenant_id = invited_user["tenant_id"]
        else:
            if not cfg.IS_MULTITENANT:
                users_count = await UsersCol.count()
                if users_count > 0:
                    return CustomResponse(
                        content="New registers are available only by invites",
                        status=State.FAILED,
                        status_code=400,
                    )

        newuser = UserOnDbModel(**user.model_dump(), role=role, tenant_id=tenant_id)
        inserted = await UsersCol.insert_one(newuser.model_dump())
        if inserted:
            await InvitedUsersCol.delete_one({"token": invite_token})
            return CustomResponse(content="Account created!")

    except Exception as err:
        log.exception(err)

    return CustomResponse(
        content="Email or password not valid",
        status=State.FAILED,
        status_code=400,
    )
