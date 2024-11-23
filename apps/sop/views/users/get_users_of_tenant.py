from apps.sop.models.collections import UsersCol
from common.logger import log


async def get_users_of_tenant(tenant_id: str):
    try:
        return await UsersCol.find_many(
            {"tenant_id": tenant_id},
            projection={
                "_id": 0,
                "user_id": 1,
                "name": 1,
                "email": 1,
                "role": 1,
                "created_on": 1,
            },
        )
    except Exception as err:
        log.exception(err)

    return []
