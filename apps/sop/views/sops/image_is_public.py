import apps.sop.models.collections as c


async def image_is_public(image_name: str):
    query = {
        "public": True,
        "quill.ops": {"$elemMatch": {"insert.image": f"/sop/images/{image_name}"}},
    }

    return bool(await c.SopsCol.count(query))
