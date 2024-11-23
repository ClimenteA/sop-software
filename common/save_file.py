import os
import shutil
from config import cfg


def save_file(file: bytes, filename: str):
    save_path = os.path.join(cfg.STORAGE_PATH, filename)

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file, buffer)

    return save_path
