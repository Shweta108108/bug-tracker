from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.user import UserOut


class CommentCreate(BaseModel):
    body: str = Field(min_length=1, max_length=10000)


class CommentOut(BaseModel):
    id: int
    issue_id: int
    author: UserOut
    body: str
    created_at: datetime
