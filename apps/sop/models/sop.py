import re
import os
from typing import Optional
from datetime import datetime
from common.save_image import save_image_sync
from pydantic import BaseModel, Field, model_validator
from apps.sop.text_utils import (
    make_text_json_safe,
    make_slug_from_text,
    optimize_text_for_search,
)


class SopOnCreateModel(BaseModel):
    title: str = Field(min_length=1)
    purpose: str
    application: str
    topics: list[str]
    content: str
    quill: dict[str, list[dict]]
    public: bool = False

    @model_validator(mode="before")
    @classmethod
    def make_images_smaller(cls, values: dict):
        if not isinstance(values.get("quill", {}).get("ops"), list):
            return values

        for ops in values["quill"]["ops"]:
            if not isinstance(ops, dict):
                continue
            if "insert" not in ops.keys():
                continue
            if not isinstance(ops["insert"], dict):
                continue
            if "image" not in ops["insert"].keys():
                continue

            image_base64 = ops["insert"]["image"]
            if re.search("data:image/.*;base64", image_base64):
                image_path = save_image_sync(image_base64, "sop")
                ops["insert"]["image"] = f"/sop/images/{os.path.basename(image_path)}"

        return values


class SopRatingOnPostModel(BaseModel):
    sop_id: str
    rating: bool


class SopOnDbModel(SopOnCreateModel):
    sop_id: str
    writers: list[str]
    tenant_id: str
    views: Optional[int] = 0
    last_viewed_on: Optional[str] = None
    rating: Optional[int] = 0
    last_update_on: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    created_on: str = None

    @model_validator(mode="before")
    @classmethod
    def clean(cls, values: dict):
        values["sop_id"] = make_slug_from_text(values["title"])
        values["title"] = make_text_json_safe(values["title"])
        values["purpose"] = make_text_json_safe(values["purpose"])
        values["application"] = make_text_json_safe(values["application"])
        values["content"] = optimize_text_for_search(values["content"])
        return values


class SopSearchOnDbModel(BaseModel):
    _id: Optional[str] = None
    search: str
    tenant_id: str
    searched_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    @model_validator(mode="before")
    @classmethod
    def make_search_id(cls, values: dict):
        values["_id"] = values["search"].lower() + values["tenant_id"]
        return values
