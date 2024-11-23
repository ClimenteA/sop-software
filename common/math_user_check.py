import uuid
import base64
import random
from datetime import datetime, timedelta
from io import BytesIO
from PIL import Image, ImageDraw
from config import get_collection, CustomResponse, State


async def create_check(collection: str):
    width = 70
    height = 20
    nr = sorted([random.randint(0, 10), random.randint(0, 10)])
    operation = random.choice(["+", "-"])
    message = f"{nr[1]} {operation} {nr[0]} = "
    solution = nr[1] + nr[0] if operation == "+" else nr[1] - nr[0]

    img = Image.new("RGB", (width, height), color="white")
    imgDraw = ImageDraw.Draw(img)
    imgDraw.text((10, 5), message, fill=(0, 0, 0))

    imgId = str(uuid.uuid4())
    buffered = BytesIO()
    img.save(buffered, format="png")
    imgbytes = buffered.getvalue()

    imgbase64 = "data:image/png;base64," + base64.b64encode(imgbytes).decode("utf-8")

    checkInfo = {
        "problem_id": imgId,
        "solution": solution,
        "imgbase64": imgbase64,
        "created_at": datetime.utcnow().isoformat(),
    }

    col = get_collection(collection)

    await col.insert_one(
        {
            "problem_id": checkInfo["problem_id"],
            "solution": checkInfo["solution"],
            "created_at": checkInfo["created_at"],
        }
    )

    # Clear checks older than 10 minutes
    refdate = (datetime.utcnow() - timedelta(minutes=10)).isoformat()
    await col.delete_many({"created_at": {"$lt": refdate}})
    checkInfo.pop("solution", None)
    return checkInfo


async def math_user_check(problem_id: str, solution: int, collection: str):
    col = get_collection(collection)
    check_ok = await col.find_one(
        {
            "problem_id": problem_id,
            "solution": solution,
        }
    )
    return CustomResponse(
        status=State.SUCCESS if check_ok else State.FAILED,
        status_code=200 if check_ok else 400,
    )
