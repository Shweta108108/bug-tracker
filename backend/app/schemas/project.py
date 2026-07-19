from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field

from app.schemas.user import UserOut


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    key: str = Field(min_length=2, max_length=10, pattern=r"^[A-Z0-9]+$")
    description: str | None = None


class ProjectOut(BaseModel):
    id: int
    name: str
    key: str
    description: str | None
    created_at: datetime
    role: Literal["member", "maintainer"]


class MemberAdd(BaseModel):
    email: EmailStr
    role: Literal["member", "maintainer"] = "member"


class MemberOut(BaseModel):
    role: Literal["member", "maintainer"]
    user: UserOut
