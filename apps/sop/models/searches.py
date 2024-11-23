from datetime import datetime
from pydantic import BaseModel, Field


class SearchModel(BaseModel):
    search: str
    searched_on: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
