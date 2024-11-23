import apps.sop.models.collections as c
from apps.sop.models.sop import SopOnDbModel, SopOnCreateModel
from common.logger import log
from common.responses import CustomResponse, State
from datetime import datetime


async def create_sop(user: dict, sop: SopOnCreateModel):
    try:
        new_sop = SopOnDbModel(
            **sop.model_dump(),
            tenant_id=user["tenant_id"],
            writers=[user["user_id"]],
            created_on=datetime.utcnow().isoformat(),
        )

        title_exists = await c.SopsCol.find_one({"sop_id": new_sop.sop_id})
        if title_exists:
            return CustomResponse(
                status=State.FAILED,
                status_code=400,
                content="This title already exists. Please modify current title or update the other SOP.",
            )

        inserted = await c.SopsCol.insert_one(new_sop.model_dump())
        if inserted:
            return CustomResponse(
                status=State.SUCCESS,
                status_code=201,
                content=new_sop.sop_id,
            )

    except Exception as err:
        log.exception(err)

    return CustomResponse(
        status=State.FAILED,
        status_code=400,
        content="Please make sure all fields are completed and try again",
    )
