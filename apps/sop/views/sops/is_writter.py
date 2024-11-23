import apps.sop.models.collections as c
from common.responses import CustomResponse, State
from apps.sop.models.user import Role


async def is_writter(user_id: str):
    if not user_id:
        return False, CustomResponse(
            status=State.FAILED,
            status_code=403,
            content="Only SME can create SOP's",
        )

    user = await c.UsersCol.find_one({"user_id": user_id})

    if user["role"] in [Role.ADMIN, Role.SME]:
        return True, CustomResponse(
            status=State.SUCCESS,
            status_code=200,
            content="SME can create SOP's",
        )

    return False, CustomResponse(
        status=State.FAILED,
        status_code=403,
        content="Only SME can create SOP's",
    )
