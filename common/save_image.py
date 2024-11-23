import re
import os
import uuid
import base64
import shutil
from PIL import Image
from .logger import log
from config import cfg


def shrink_image_sync(imgpath: str):
    image = Image.open(imgpath)
    target_size = 500 * 1024  # 500 KB

    initial_image_size = os.path.getsize(imgpath)
    if initial_image_size <= target_size:
        return imgpath

    quality_range = range(90, 10, -10)
    for quality in quality_range:
        image.save(imgpath, optimize=True, quality=quality)

        current_image_size = os.path.getsize(imgpath)

        if current_image_size <= target_size:
            break

        if current_image_size == initial_image_size:
            break

        initial_image_size = current_image_size

        log.info(
            f"Initial size: {initial_image_size}, current size: {current_image_size}, target_size: {target_size}, quality: {quality}"
        )

    return imgpath


async def shrink_image(imgpath: str):
    return shrink_image_sync(imgpath)


def get_image_extension_sync(img):
    if isinstance(img, str):
        extension = re.search(r"data:image/(.*);base64", img)
        if extension:
            ext = "." + extension.group(1)
            if ext in [".jpeg", ".jpg", ".png"]:
                return ext

    if not hasattr(img, "filename"):
        return None
    if not hasattr(img, "file"):
        return None
    extension = [ext for ext in [".jpeg", ".jpg", ".png"] if img.filename.endswith(ext)]
    if not extension:
        return None
    return extension[0]


async def get_image_extension(img):
    return get_image_extension_sync(img)


def get_image_save_path_sync(img, extension, save_path):
    save_path = os.path.join(cfg.STORAGE_PATH, save_path)
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    filename = str(uuid.uuid4()) + extension
    image_save_path = os.path.join(save_path, filename)

    if isinstance(img, str):
        imgbase64data = re.search(r"data:image/.*;base64,(.*)?", img)
        if imgbase64data:
            with open(image_save_path, "wb") as f:
                f.write(base64.urlsafe_b64decode(imgbase64data.group(1)))
    else:
        with open(image_save_path, "wb") as buffer:
            shutil.copyfileobj(img.file, buffer)

    return image_save_path


async def get_image_save_path(img, extension, save_path):
    return get_image_save_path_sync(img, extension, save_path)


async def save_image(img, save_path: str):
    extension = await get_image_extension(img)
    if not extension:
        return None

    image_save_path = await get_image_save_path(img, extension, save_path)
    image_save_path = await shrink_image(image_save_path)

    return image_save_path


def save_image_sync(img, save_path: str):
    extension = get_image_extension_sync(img)
    if not extension:
        return None

    image_save_path = get_image_save_path_sync(img, extension, save_path)
    image_save_path = shrink_image_sync(image_save_path)
    assert os.path.exists(image_save_path)
    return image_save_path
