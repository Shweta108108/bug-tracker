from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.dao import user_dao
from app.db import get_db
from app.models.enums import IssuePriority, IssueStatus
from app.models.issue import Issue
from app.models.user import User
from app.schemas.common import Paginated
from app.schemas.issue import IssueCreate, IssueOut, IssueUpdate
from app.schemas.user import UserOut
from app.services import issue_service

router = APIRouter(prefix="/api", tags=["issues"])


def _issue_out(issue: Issue, reporter: User, assignee: User | None) -> IssueOut:
    return IssueOut(
        id=issue.id,
        project_id=issue.project_id,
        title=issue.title,
        description=issue.description,
        status=issue.status,
        priority=issue.priority,
        reporter=UserOut.model_validate(reporter),
        assignee=UserOut.model_validate(assignee) if assignee else None,
        created_at=issue.created_at,
        updated_at=issue.updated_at,
    )


def _issue_out_from_id(db: Session, issue: Issue) -> IssueOut:
    reporter = user_dao.get_by_id(db, issue.reporter_id)
    assignee = user_dao.get_by_id(db, issue.assignee_id) if issue.assignee_id else None
    return _issue_out(issue, reporter, assignee)


@router.get("/projects/{project_id}/issues", response_model=Paginated[IssueOut])
def list_issues(
    project_id: int,
    q: str | None = None,
    status: IssueStatus | None = None,
    priority: IssuePriority | None = None,
    assignee_id: int | None = None,
    sort: str = "-created_at",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Paginated[IssueOut]:
    rows, total = issue_service.list_issues(
        db,
        project_id=project_id,
        user_id=user.id,
        q=q,
        status=status.value if status else None,
        priority=priority.value if priority else None,
        assignee_id=assignee_id,
        sort=sort,
        page=page,
        page_size=page_size,
    )
    items = [_issue_out(issue, reporter, assignee) for issue, reporter, assignee in rows]
    return Paginated[IssueOut](items=items, total=total, page=page, page_size=page_size)


@router.post("/projects/{project_id}/issues", response_model=IssueOut, status_code=201)
def create_issue(
    project_id: int,
    payload: IssueCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> IssueOut:
    issue = issue_service.create_issue(
        db,
        project_id=project_id,
        reporter=user,
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        assignee_id=payload.assignee_id,
    )
    return _issue_out_from_id(db, issue)


@router.get("/issues/{issue_id}", response_model=IssueOut)
def get_issue(
    issue_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> IssueOut:
    issue, _membership = issue_service.get_issue_with_membership(db, issue_id=issue_id, user_id=user.id)
    return _issue_out_from_id(db, issue)


@router.patch("/issues/{issue_id}", response_model=IssueOut)
def patch_issue(
    issue_id: int,
    payload: IssueUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> IssueOut:
    issue, membership = issue_service.get_issue_with_membership(db, issue_id=issue_id, user_id=user.id)
    patch = payload.model_dump(exclude_unset=True)
    issue = issue_service.update_issue(db, issue=issue, user=user, membership=membership, patch=patch)
    return _issue_out_from_id(db, issue)


@router.delete("/issues/{issue_id}", status_code=204)
def delete_issue(
    issue_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> None:
    issue, membership = issue_service.get_issue_with_membership(db, issue_id=issue_id, user_id=user.id)
    issue_service.delete_issue(db, issue=issue, membership=membership)
