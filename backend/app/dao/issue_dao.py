from sqlalchemy import asc, case, desc, func, select
from sqlalchemy.orm import Session, aliased

from app.models.enums import IssuePriority
from app.models.issue import Issue
from app.models.user import User

_ReporterUser = aliased(User)
_AssigneeUser = aliased(User)

_PRIORITY_RANK = case(
    (Issue.priority == IssuePriority.CRITICAL.value, 4),
    (Issue.priority == IssuePriority.HIGH.value, 3),
    (Issue.priority == IssuePriority.MEDIUM.value, 2),
    (Issue.priority == IssuePriority.LOW.value, 1),
    else_=0,
)

# Whitelist of sortable fields -> ordering expression, to avoid letting the
# `sort` query param select an arbitrary column.
_SORT_FIELDS = {
    "created_at": Issue.created_at,
    "priority": _PRIORITY_RANK,
    "status": Issue.status,
}


def create(
    db: Session,
    *,
    project_id: int,
    title: str,
    description: str | None,
    priority: str,
    reporter_id: int,
    assignee_id: int | None,
) -> Issue:
    issue = Issue(
        project_id=project_id,
        title=title,
        description=description,
        priority=priority,
        reporter_id=reporter_id,
        assignee_id=assignee_id,
    )
    db.add(issue)
    db.flush()
    return issue


def get_by_id(db: Session, issue_id: int) -> Issue | None:
    return db.get(Issue, issue_id)


def delete(db: Session, issue: Issue) -> None:
    db.delete(issue)


def get_with_users(db: Session, issue_id: int) -> tuple[Issue, User, User | None] | None:
    stmt = (
        select(Issue, _ReporterUser, _AssigneeUser)
        .join(_ReporterUser, _ReporterUser.id == Issue.reporter_id)
        .outerjoin(_AssigneeUser, _AssigneeUser.id == Issue.assignee_id)
        .where(Issue.id == issue_id)
    )
    return db.execute(stmt).first()


def _apply_filters(stmt, *, project_id: int, q: str | None, status: str | None, priority: str | None, assignee_id: int | None):
    stmt = stmt.where(Issue.project_id == project_id)
    if status:
        stmt = stmt.where(Issue.status == status)
    if priority:
        stmt = stmt.where(Issue.priority == priority)
    if assignee_id is not None:
        stmt = stmt.where(Issue.assignee_id == assignee_id)
    if q:
        stmt = stmt.where(Issue.title.ilike(f"%{q}%"))
    return stmt


def list_issues(
    db: Session,
    *,
    project_id: int,
    q: str | None,
    status: str | None,
    priority: str | None,
    assignee_id: int | None,
    sort: str,
    page: int,
    page_size: int,
) -> tuple[list[tuple[Issue, User, User | None]], int]:
    page_size = min(max(page_size, 1), 100)
    page = max(page, 1)

    filters = dict(project_id=project_id, q=q, status=status, priority=priority, assignee_id=assignee_id)

    count_stmt = _apply_filters(select(Issue), **filters)
    total = db.scalar(select(func.count()).select_from(count_stmt.subquery()))

    sort_key = sort.lstrip("-")
    order_column = _SORT_FIELDS.get(sort_key, Issue.created_at)
    direction = desc if sort.startswith("-") else asc

    stmt = _apply_filters(
        select(Issue, _ReporterUser, _AssigneeUser)
        .join(_ReporterUser, _ReporterUser.id == Issue.reporter_id)
        .outerjoin(_AssigneeUser, _AssigneeUser.id == Issue.assignee_id),
        **filters,
    )
    stmt = stmt.order_by(direction(order_column), Issue.id).offset((page - 1) * page_size).limit(page_size)

    rows = list(db.execute(stmt).all())
    return rows, total
