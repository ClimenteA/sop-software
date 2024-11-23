from typing import Any
from enum import StrEnum
from dataclasses import dataclass


class State(StrEnum):
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class CustomResponse:
    content: Any = None
    status_code: int = 200
    status: State = State.SUCCESS
    extra: Any = None

    def __post_init__(self):
        if not str(self.status_code).startswith(("3", "2", "1")):
            self.status = State.FAILED
