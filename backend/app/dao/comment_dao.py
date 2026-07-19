from sqlalchemy import select
from sqlalchemy.orm import Session, aliased

from app.models.comment import Comment
from app.models.user import User

_AuthorUser = aliased(User)


def create(db: Session, *, issue_id: int, author_id: int, body: str) -> Comment:
    comment = Comment(issue_id=issue_id, author_id=author_id, body=body)
    db.add(comment)
    db.flush()
    return comment


def list_for_issue(db: Session, issue_id: int) -> list[tuple[Comment, User]]:
    stmt = (
        select(Comment, _AuthorUser)
        .join(_AuthorUser, _AuthorUser.id == Comment.author_id)
        .where(Comment.issue_id == issue_id)
        .order_by(Comment.created_at.asc(), Comment.id.asc())
    )
    return list(db.execute(stmt).all())
