from sqlalchemy.orm import Session

from app.dao import comment_dao
from app.models.comment import Comment
from app.models.user import User
from app.services import issue_service


def add_comment(db: Session, *, issue_id: int, author: User, body: str) -> tuple[Comment, User]:
    issue_service.get_issue_with_membership(db, issue_id=issue_id, user_id=author.id)
    comment = comment_dao.create(db, issue_id=issue_id, author_id=author.id, body=body)
    db.commit()
    db.refresh(comment)
    return comment, author


def list_comments(db: Session, *, issue_id: int, requester: User) -> list[tuple[Comment, User]]:
    issue_service.get_issue_with_membership(db, issue_id=issue_id, user_id=requester.id)
    return comment_dao.list_for_issue(db, issue_id)
