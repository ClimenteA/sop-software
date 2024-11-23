from apps.sop.models.collections import InvitedUsersCol, UsersCol


async def get_info_from_invite_token(invite_token: str):
    token_info = await InvitedUsersCol.find_one({"token": invite_token})
    owner = await UsersCol.find_one({"user_id": token_info["tenant_id"]})
    return owner["company"], token_info["email"]
