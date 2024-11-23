from apps.sop.models.collections import SopsCol


async def get_topics(tenant_id: str):
    if tenant_id:
        query = {"tenant_id": tenant_id}
    else:
        query = {"public": True}

    pipeline = [
        {"$match": query},
        {"$unwind": "$topics"},
        {"$group": {"_id": "$topics"}},
        {"$project": {"_id": 0, "topic": "$_id"}},
    ]
    result = await SopsCol.aggregate(pipeline)
    if not result:
        return []

    return sorted([r["topic"] for r in result])
