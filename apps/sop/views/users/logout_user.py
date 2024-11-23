from common.jwt import blacklist_token
from common.responses import CustomResponse, State


async def logout_user(token: str):
    blacklisted = await blacklist_token(token)
    if blacklisted:
        return CustomResponse(content="Token blacklisted")
    return CustomResponse(
        content="Invalid token",
        status=State.FAILED,
        status_code=400,
    )
