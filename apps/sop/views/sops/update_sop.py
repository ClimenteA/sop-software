import apps.sop.models.collections as c
from apps.sop.models.sop import SopOnDbModel, SopOnCreateModel
from common.logger import log
from common.responses import CustomResponse, State
from .is_writter import is_writter
from .get_tenant_id import get_tenant_id


async def update_sop(user_id: str, sop_id: str, sop: SopOnCreateModel):
    try:
        is_writer, response = await is_writter(user_id)
        if not is_writer:
            return response

        tenant_id = await get_tenant_id(user_id)

        sopindb = await c.SopsCol.find_one({"sop_id": sop_id, "tenant_id": tenant_id})
        if not sopindb:
            return CustomResponse(
                status=State.FAILED,
                status_code=404,
                content="This SOP doesn't exist",
            )

        if user_id not in sopindb["writers"]:
            sopindb["writers"].append(user_id)

        new_sop = {**sopindb, **sop.model_dump()}
        updated_sop = SopOnDbModel(**new_sop)

        updated = await c.SopsCol.update_one(
            {"sop_id": sop_id, "tenant_id": tenant_id}, data=updated_sop.model_dump()
        )
        if updated:
            return CustomResponse(status=State.SUCCESS, status_code=200, content=sop_id)

    except Exception as err:
        log.exception(err)

    return CustomResponse(
        status=State.FAILED,
        status_code=400,
        content="Please make sure all fields are completed and try again",
    )
