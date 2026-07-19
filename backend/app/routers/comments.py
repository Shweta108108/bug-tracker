from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db import get_db
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentOut
from app.schemas.user import UserOut
from app.services import comment_service

router = APIRouter(prefix="/api/issues", tags=["comments"])


@router.get("/{issue_id}/comments", response_model=list[CommentOut])
def list_comments(
    issue_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> list[CommentOut]:
    rows = comment_service.list_comments(db, issue_id=issue_id, requester=user)
    return [
        CommentOut(
            id=comment.id,
            issue_id=comment.issue_id,
            author=UserOut.model_validate(author),
            body=comment.body,
            created_at=comment.created_at,
        )
        for comment, author in rows
    ]


@router.post("/{issue_id}/comments", response_model=CommentOut, status_code=201)
def add_comment(
    issue_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> CommentOut:
    comment, author = comment_service.add_comment(db, issue_id=issue_id, author=user, body=payload.body)
    return CommentOut(
        id=comment.id,
        issue_id=comment.issue_id,
        author=UserOut.model_validate(author),
        body=comment.body,
        created_at=comment.created_at,
    )
