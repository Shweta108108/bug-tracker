from sqlalchemy.orm import Session

from app.core.exceptions import AppError, ForbiddenError, NotFoundError
from app.dao import issue_dao, project_dao
from app.models.enums import ProjectRole
from app.models.issue import Issue
from app.models.project_member import ProjectMember
from app.models.user import User
from app.services import authz

_RESTRICTED_FIELDS = {"status", "assignee_id"}


def _assert_assignee_is_member(db: Session, *, project_id: int, assignee_id: int | None) -> None:
    if assignee_id is None:
        return
    if project_dao.get_membership(db, project_id=project_id, user_id=assignee_id) is None:
        raise AppError(
            "Assignee must be a member of this project.",
            details={"field": "assignee_id"},
            code="ASSIGNEE_NOT_MEMBER",
        )


def create_issue(
    db: Session,
    *,
    project_id: int,
    reporter: User,
    title: str,
    description: str | None,
    priority: str,
    assignee_id: int | None,
) -> Issue:
    authz.get_membership_or_403(db, project_id=project_id, user_id=reporter.id)
    _assert_assignee_is_member(db, project_id=project_id, assignee_id=assignee_id)

    issue = issue_dao.create(
        db,
        project_id=project_id,
        title=title,
        description=description,
        priority=priority,
        reporter_id=reporter.id,
        assignee_id=assignee_id,
    )
    db.commit()
    db.refresh(issue)
    return issue


def get_issue_with_membership(db: Session, *, issue_id: int, user_id: int) -> tuple[Issue, ProjectMember]:
    issue = issue_dao.get_by_id(db, issue_id)
    if issue is None:
        raise NotFoundError("Issue not found.")
    membership = authz.get_membership_or_403(db, project_id=issue.project_id, user_id=user_id)
    return issue, membership


def update_issue(
    db: Session, *, issue: Issue, user: User, membership: ProjectMember, patch: dict
) -> Issue:
    is_maintainer = membership.role == ProjectRole.MAINTAINER.value
    touched_restricted = _RESTRICTED_FIELDS.intersection(patch.keys())

    if not is_maintainer:
        if touched_restricted:
            raise ForbiddenError("Only maintainers can change status or assignee.")
        if issue.reporter_id != user.id:
            raise ForbiddenError("You can only edit issues you reported.")

    if "assignee_id" in patch:
        _assert_assignee_is_member(db, project_id=issue.project_id, assignee_id=patch["assignee_id"])

    for field, value in patch.items():
        setattr(issue, field, value)

    db.commit()
    db.refresh(issue)
    return issue


def delete_issue(db: Session, *, issue: Issue, membership: ProjectMember) -> None:
    authz.assert_maintainer(membership)
    issue_dao.delete(db, issue)
    db.commit()


def list_issues(
    db: Session,
    *,
    project_id: int,
    user_id: int,
    q: str | None,
    status: str | None,
    priority: str | None,
    assignee_id: int | None,
    sort: str,
    page: int,
    page_size: int,
):
    authz.get_membership_or_403(db, project_id=project_id, user_id=user_id)
    return issue_dao.list_issues(
        db,
        project_id=project_id,
        q=q,
        status=status,
        priority=priority,
        assignee_id=assignee_id,
        sort=sort,
        page=page,
        page_size=page_size,
    )
