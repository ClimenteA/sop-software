from apps.sop.models.collections import SopsCol


async def get_titles(tenant_id: str):
    if tenant_id:
        query = {"tenant_id": tenant_id}
    else:
        query = {"public": True}

    result = await SopsCol.find_many(query, projection={"_id": 0, "title": 1})
    if not result:
        return []

    return sorted([r["title"] for r in result])
