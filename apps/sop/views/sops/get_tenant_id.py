import apps.sop.models.collections as c


async def get_tenant_id(user_id: str):
    user = await c.UsersCol.find_one({"user_id": user_id}, projection={"tenant_id": 1})
    return user["tenant_id"]
