import base64
from common.logger import log


async def image_to_base64(image_path: str):
    try:
        with open(image_path, "rb") as file_contents:
            b64_string = base64.b64encode(file_contents.read())
        image_base64 = f"data:image/*;base64," + b64_string.decode("utf-8")
        return image_base64
    except Exception as err:
        log.exception(err)
    return None
