import uuid
from enum import StrEnum
from typing import Optional
from datetime import datetime, timezone
from typing_extensions import Annotated
from pydantic import BaseModel, Field, AfterValidator, model_validator
from common.validators import get_encrypted_password, get_lower_email

StrLowerEmail = Annotated[str, AfterValidator(get_lower_email)]


class UserOnLoginModel(BaseModel):
    email: StrLowerEmail
    password: str


class UserOnRegisterModel(UserOnLoginModel):
    name: str
    company: str


class UserOnAvatarModel(BaseModel):
    avatar: Optional[str] = None


class Role(StrEnum):
    READER = "reader"
    SME = "sme"
    ADMIN = "admin"


class UserOnDbModel(UserOnAvatarModel, UserOnRegisterModel):
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: Role = Role.READER
    created_on: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_on: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    tenant_id: Optional[str] = None

    @model_validator(mode="after")
    def clean(self):
        if self.tenant_id is None:
            self.tenant_id = self.user_id
        self.password = get_encrypted_password(self.password)
        return self


class UserOnInviteModel(BaseModel):
    email: StrLowerEmail
    role: Role

    @model_validator(mode="before")
    @classmethod
    def clean(cls, data: dict):
        data["role"] = data["role"].lower()
        return data


class UserOnInviteInDbModel(UserOnInviteModel):
    tenant_id: str
    invited_on: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    token: str = Field(default_factory=lambda: str(uuid.uuid4()))


class MessageAdminModel(BaseModel):
    email: StrLowerEmail
    message: str
    added_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
