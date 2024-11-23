from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from apps.sop.models.collections import MessagesAdminCol
from apps.sop.models.user import MessageAdminModel
from common.render_template import render_template
from common.responses import CustomResponse, State
from common.logger import log


router = APIRouter(tags=["SOPLegal"], prefix="/sop")


@router.get("/contact", response_class=HTMLResponse)
async def get_contact_template(request: Request):
    return await render_template(request, "sop/contact.html")


@router.post("/contact", response_model=CustomResponse)
async def save_message_for_admin(message: MessageAdminModel):
    try:
        await MessagesAdminCol.insert_one(message.model_dump())
        return CustomResponse(content="Message sent")
    except Exception as err:
        log.exception(err)
        return CustomResponse(status=State.FAILED, status_code=500)


@router.get("/about", response_class=HTMLResponse)
async def sop_get_about_us_template(request: Request):
    return await render_template(request, "sop/pabout.html")


@router.get("/cookies", response_class=HTMLResponse)
async def sop_get_cookies_template(request: Request):
    return await render_template(request, "sop/pcookies.html")


@router.get("/gdpr", response_class=HTMLResponse)
async def sop_get_gdpr_template(request: Request):
    return await render_template(request, "sop/pgdpr.html")


@router.get("/toc", response_class=HTMLResponse)
async def sop_get_toc_template(request: Request):
    return await render_template(request, "sop/ptoc.html")


@router.get(
    "/increase-productivity-with-standard-operating-procedure-sop-software",
    response_class=HTMLResponse,
)
async def sop_why_sop_template(request: Request):
    return await render_template(request, "sop/why_sop.html")
