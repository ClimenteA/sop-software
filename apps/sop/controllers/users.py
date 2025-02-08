from typing import Annotated
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import APIRouter, Cookie, Response, Request
from apps.sop.models.user import (
    UserOnAvatarModel,
    UserOnLoginModel,
    UserOnRegisterModel,
    UserOnInviteModel,
    Role,
)
from apps.sop.models.collections import UsersCol
from apps.sop.models.collections import SOPCol
import apps.sop.views.users as views
from common.responses import CustomResponse, State
from common.jwt import get_user_id_from_token
from common.render_template import render_template
from apps.sop.text_utils import get_word_cloud_svg
from config import cfg


router = APIRouter(tags=[SOPCol.Users], prefix="/sop")


@router.get("/login", response_class=HTMLResponse)
async def get_login_template(
    request: Request,
    token: Annotated[str | None, Cookie()] = None,
):
    user_id = await get_user_id_from_token(token)
    if user_id is not None:
        return RedirectResponse("/sop/my-account")
    return await render_template(request, "sop/login.html", context={"logged": user_id})


@router.post("/login", response_model=CustomResponse)
async def login_user(creds: UserOnLoginModel, response: Response):
    result = await views.login_user(creds)
    response.status_code = result.status_code
    response.set_cookie(key="token", value=result.content)
    return result


@router.get("/logout")
async def logout_user(
    as_json: bool = False, token: Annotated[str | None, Cookie()] = None
):
    result = await views.logout_user(token)
    return result if as_json else RedirectResponse("/sop/login")


@router.get("/register", response_class=HTMLResponse)
async def get_register_template(
    request: Request,
    invite_token: str = None,
    token: Annotated[str | None, Cookie()] = None,
):
    user_id = await get_user_id_from_token(token)
    if user_id is not None:
        if invite_token is not None:
            await views.logout_user(token)
        else:
            return RedirectResponse("/sop/my-account")

    company, invited_email = None, None
    if invite_token is not None:
        await views.logout_user(token)
        company, invited_email = await views.get_info_from_invite_token(invite_token)

    if not cfg.IS_MULTITENANT and invite_token is None:
        users_count = await UsersCol.count()
        if users_count > 0:
            return RedirectResponse("/sop/login")

    return await render_template(
        request,
        "sop/register.html",
        context={
            "logged": user_id,
            "invite_token": invite_token,
            "company": company,
            "email": invited_email,
            "demo_account": cfg.DEMO_ACCOUNT,
        },
    )


@router.post("/register", response_model=CustomResponse)
async def register_user(
    user: UserOnRegisterModel,
    invite_token: str = None,
):
    result = await views.register_user(user, invite_token)
    return result


@router.get("/add-new-user", response_class=HTMLResponse)
async def get_add_new_user_template(
    request: Request,
    token: Annotated[str | None, Cookie()] = None,
):
    user_id = await get_user_id_from_token(token)
    if user_id is None:
        return RedirectResponse("/sop/my-account")
    return await render_template(
        request, "sop/add_new_user.html", context={"logged": user_id}
    )


@router.post("/add-new-user", response_model=CustomResponse)
async def add_new_user_by_admin(
    invited_user: UserOnInviteModel,
    token: Annotated[str | None, Cookie()] = None,
):
    user_id = await get_user_id_from_token(token)
    if user_id is None:
        return CustomResponse(
            content="Please login first", status_code=403, status=State.FAILED
        )
    user = await views.get_user_by_id(user_id)
    if user["role"] != Role.ADMIN:
        return CustomResponse(
            content="Only admins can add more users",
            status_code=403,
            status=State.FAILED,
        )

    result = await views.add_new_user_by_admin(user["tenant_id"], invited_user)
    return result


@router.get("/update-account", response_model=CustomResponse)
async def get_update_account_template(
    request: Request, token: Annotated[str | None, Cookie()] = None
):
    user_id = await get_user_id_from_token(token)
    if user_id is None:
        return RedirectResponse("/sop/login")
    user = await views.get_user_by_id(user_id)
    return await render_template(
        request, "sop/account_update.html", context={"logged": user_id, "user": user}
    )


@router.put("/update-account", response_model=CustomResponse)
async def update_account(
    avatar: UserOnAvatarModel, token: Annotated[str | None, Cookie()] = None
):
    user_id = await get_user_id_from_token(token)
    if user_id is None:
        return CustomResponse(
            status=State.FAILED, status_code=403, content="Unauthorized"
        )
    return await views.update_avatar(user_id, avatar)


@router.get("/delete-account", response_model=CustomResponse)
async def delete_account(token: Annotated[str | None, Cookie()] = None):
    user_id = await get_user_id_from_token(token)
    if user_id is None:
        return CustomResponse(
            status=State.FAILED, status_code=403, content="Unauthorized"
        )
    await views.delete_account(user_id)
    return RedirectResponse("/sop/login")


@router.get("/delete-account/{user_id_to_delete}", response_model=CustomResponse)
async def delete_account(
    user_id_to_delete: str, token: Annotated[str | None, Cookie()] = None
):
    user_id = await get_user_id_from_token(token)
    if user_id is None:
        return CustomResponse(
            status=State.FAILED, status_code=403, content="Unauthorized"
        )

    user = await views.get_user_by_id(user_id)
    if user["role"] == Role.ADMIN:
        await views.delete_account(user_id_to_delete)

    return RedirectResponse("/sop/my-account?activeTab=users#tabs")


@router.get("/my-account")
async def get_account_template(
    request: Request,
    activeTab: str = "stats",
    token: Annotated[str | None, Cookie()] = None,
):
    user_id = await get_user_id_from_token(token)
    if user_id is None:
        return RedirectResponse("/sop/login")

    user = await views.get_user_by_id(user_id)
    users = await views.get_users_of_tenant(user["tenant_id"])
    sops = await views.get_user_sops(user_id)
    searches = await views.get_searches(user["tenant_id"])
    count_stats = await views.get_count_stats(user["tenant_id"])
    sops_to_improve = await views.get_sops_to_improve(user["tenant_id"])

    search_cloud = None
    if searches:
        text = "".join([s["search"] for s in searches])
        search_cloud = get_word_cloud_svg(text)

    result = {
        "logged": user_id,
        "user": user,
        "users": users,
        "sops": sops,
        "searches": searches,
        "search_cloud": search_cloud,
        "count_stats": count_stats,
        "sops_to_improve": sops_to_improve,
        "activeTab": activeTab,
    }

    return await render_template(request, "sop/account.html", context=result)
