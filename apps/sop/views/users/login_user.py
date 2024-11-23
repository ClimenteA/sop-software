from apps.sop.models.user import UserOnLoginModel
from apps.sop.models.collections import UsersCol, SOPCol
from common.password import encrypt
from common.responses import CustomResponse, State
from common.jwt import get_token_for_user_id
from common.logger import log


async def login_user(creds: UserOnLoginModel):
    try:
        user = await UsersCol.find_one(
            {"email": creds.email, "password": encrypt(creds.password)},
            projection={"_id": 0, "user_id": 1},
        )
        if not user:
            return CustomResponse(
                content="Invalid email or password",
                status=State.FAILED,
                status_code=400,
            )

        token = await get_token_for_user_id(
            user["user_id"],
            users_col=SOPCol.Users,
            blacktoken_col=SOPCol.TokenBlackList,
        )

        return CustomResponse(content=token)

    except Exception as err:
        log.exception(err)

    return CustomResponse(
        content="Please try again.",
        status=State.FAILED,
        status_code=500,
    )
