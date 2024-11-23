import os
import json
from typing import Annotated
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi import APIRouter, UploadFile, Cookie, Request
from common.save_image import save_image
from common.jwt import get_user_id_from_token
from common.render_template import render_template
from apps.sop.models.user import Role
from apps.sop.models.collections import SOPCol
import apps.sop.views.sops as views
from apps.sop.views.users import get_user_by_id
from common.responses import CustomResponse, State
from apps.sop.models.sop import SopOnCreateModel, SopRatingOnPostModel
from apps.sop.models.collections import UsersCol
from config import cfg


router = APIRouter(tags=[SOPCol.Sops], prefix="/sop")


@router.get("/add-sop", response_class=HTMLResponse)
async def get_add_sop_template(
    request: Request,
    token: Annotated[str | None, Cookie()] = None,
):
    user_id = await get_user_id_from_token(token)
    if user_id is None:
        return RedirectResponse("/sop/login")

    user = await get_user_by_id(user_id)
    if user["role"] not in [Role.ADMIN, Role.SME]:
        return RedirectResponse("/sop/login")

    all_topics = await views.get_topics(user["tenant_id"] if user else None)

    return await render_template(
        request,
        "sop/add_sop.html",
        context={
            "logged": user_id,
            "sop": None,
            "is_writer": True,
            "all_topics": all_topics,
        },
    )


@router.post("/add-sop", response_model=CustomResponse)
async def create_sop(
    sop: SopOnCreateModel,
    token: Annotated[str | None, Cookie()] = None,
):
    user_id = await get_user_id_from_token(token)
    if user_id is None:
        return CustomResponse(
            content="Token invalid", status=State.FAILED, status_code=403
        )

    user = await get_user_by_id(user_id)
    if user["role"] not in [Role.ADMIN, Role.SME]:
        return CustomResponse(
            content="Only Admins and SME can create SOP's",
            status=State.FAILED,
            status_code=403,
        )

    result = await views.create_sop(user, sop)
    return result


@router.get("/view-sop/{sop_id}")
async def get_sop_view_template(
    request: Request,
    sop_id: str,
    token: Annotated[str | None, Cookie()] = None,
):
    user_id = await get_user_id_from_token(token)
    result = await views.get_sop_by_id(sop_id, user_id, count_view=True)
    if result is None:
        return RedirectResponse("/sop/sops")

    is_writer, _ = await views.is_writter(user_id)
    auser = await UsersCol.find_one({"tenant_id": result["tenant_id"]})
    result["quill"] = json.dumps(result["quill"])

    return await render_template(
        request,
        "sop/sop_view.html",
        context={
            "sop": {"company": auser["company"], **result},
            "logged": user_id,
            "is_writer": is_writer,
        },
    )


@router.get("/sop-json/{sop_id}")
async def get_sop_json(
    sop_id: str,
    token: Annotated[str | None, Cookie()] = None,
):
    user_id = await get_user_id_from_token(token)
    result = await views.get_sop_by_id(sop_id, user_id, count_view=True)
    if result is None:
        return CustomResponse(
            status=State.FAILED, content="SOP not found", status_code=404
        )

    return CustomResponse(status=State.SUCCESS, content=result, status_code=200)


@router.post("/rate-sop")
async def rate_sop(
    rating: SopRatingOnPostModel, token: Annotated[str | None, Cookie()] = None
):
    user_id = await get_user_id_from_token(token)
    return await views.rate_sop(user_id, rating)


@router.get("/update-sop/{sop_id}")
async def get_sop_update_template(
    request: Request,
    sop_id: str,
    token: Annotated[str | None, Cookie()] = None,
):
    user_id = await get_user_id_from_token(token)
    if user_id is None:
        return RedirectResponse("/sop/login")

    result = await views.get_sop_by_id(sop_id, user_id)
    if result is None:
        return RedirectResponse("/sop/sops")

    is_writer, _ = await views.is_writter(user_id)
    user = await get_user_by_id(user_id)
    all_topics = await views.get_topics(user["tenant_id"] if user else None)

    return await render_template(
        request,
        "sop/add_sop.html",
        context={
            "sop": result,
            "logged": user_id,
            "is_writer": is_writer,
            "all_topics": all_topics,
        },
    )


@router.put("/update-sop/{sop_id}", response_model=CustomResponse)
async def update_sop(
    sop_id: str,
    sop: SopOnCreateModel,
    token: Annotated[str | None, Cookie()] = None,
):
    user_id = await get_user_id_from_token(token)
    if user_id is None:
        return CustomResponse(
            content="Token invalid", status=State.FAILED, status_code=403
        )
    result = await views.update_sop(user_id, sop_id, sop)
    return result


@router.get("/sops")
async def get_sops_response(
    request: Request,
    page: int = 1,
    search: str = None,
    topic: str = None,
    token: Annotated[str | None, Cookie()] = None,
):
    user_id = await get_user_id_from_token(token)
    user = await get_user_by_id(user_id)
    sops = await views.get_sops(
        page, search, topic, user["tenant_id"] if user else None
    )
    # NOTE: auto-complete value was selected with title slug
    if not isinstance(sops, list):
        return RedirectResponse(f"/sop/view-sop/{sops['sop_id']}")

    topics = await views.get_topics(user["tenant_id"] if user else None)
    all_titles = await views.get_titles(user["tenant_id"] if user else None)

    next_page_url = f"/sop/sops?page={page + 1 if page > 0 else 1}&topic={topic or ''}&search={search or ''}"
    prev_page_url = f"/sop/sops?page={page - 1 if page > 0 else 1}&topic={topic or ''}&search={search or ''}"

    result = {
        "sops": sops,
        "logged": user_id,
        "page": page,
        "search": search,
        "topics": topics,
        "all_titles": all_titles,
        "selected_topic": topic,
        "next_page_url": next_page_url,
        "prev_page_url": prev_page_url,
    }
    return await render_template(request, "sop/sops.html", context=result)


@router.post("/image-to-base64")
async def image_to_base64(
    images: list[UploadFile],
    token: Annotated[str | None, Cookie()] = None,
):
    user_id = await get_user_id_from_token(token)
    if user_id is None:
        return CustomResponse(
            content="Token invalid", status=State.FAILED, status_code=403
        )
    image_path = await save_image(images[0], "sop")
    result = await views.image_to_base64(image_path)
    return result


@router.get("/images/{image_name}", response_class=FileResponse)
async def sop_get_image_from_storage(
    image_name: str,
    token: Annotated[str | None, Cookie()] = None,
):
    public_img = await views.image_is_public(image_name)

    if public_img is False:
        user_id = await get_user_id_from_token(token)
        if user_id is None:
            return FileResponse("./public/notimg.svg", status_code=404)

    filepath = f"{cfg.STORAGE_PATH}/sop/{image_name}"

    if os.path.exists(filepath):
        return FileResponse(filepath, status_code=200)

    return FileResponse("./public/notimg.svg", status_code=404)


@router.post("/upload-image")
async def upload_image(
    images: list[UploadFile],
    token: Annotated[str | None, Cookie()] = None,
):
    user_id = await get_user_id_from_token(token)
    if user_id is None:
        return CustomResponse(
            content="Token invalid", status=State.FAILED, status_code=403
        )
    image_path = await save_image(images[0], "sop")
    return f"/sop/images/{os.path.basename(image_path)}"


@router.get("/delete-sop/{sop_id}", response_model=CustomResponse)
async def delete_sop(
    sop_id: str,
    token: Annotated[str | None, Cookie()] = None,
):
    user_id = await get_user_id_from_token(token)
    if user_id is None:
        return CustomResponse(
            content="Token invalid", status=State.FAILED, status_code=403
        )
    await views.delete_sop(user_id, sop_id)
    return RedirectResponse("/sop/sops")
