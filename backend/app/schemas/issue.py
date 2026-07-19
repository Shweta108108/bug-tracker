from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.user import UserOut


class IssueCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    priority: Literal["low", "medium", "high", "critical"] = "medium"
    assignee_id: int | None = None


class IssueUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    status: Literal["open", "in_progress", "resolved", "closed"] | None = None
    priority: Literal["low", "medium", "high", "critical"] | None = None
    assignee_id: int | None = None


class IssueOut(BaseModel):
    id: int
    project_id: int
    title: str
    description: str | None
    status: str
    priority: str
    reporter: UserOut
    assignee: UserOut | None
    created_at: datetime
    updated_at: datetime
