from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError
from app.dao import project_dao
from app.models.enums import ProjectRole
from app.models.project import Project
from app.models.project_member import ProjectMember


def get_project_or_404(db: Session, project_id: int) -> Project:
    project = project_dao.get_by_id(db, project_id)
    if project is None:
        raise NotFoundError("Project not found.")
    return project


def get_membership_or_403(db: Session, *, project_id: int, user_id: int) -> ProjectMember:
    """Single source of truth for "is this user a member of this project".

    Reused both for project-scoped routes and issue-derived routes (which
    look up project_id from the issue first) so the check lives in one place.
    """
    get_project_or_404(db, project_id)
    membership = project_dao.get_membership(db, project_id=project_id, user_id=user_id)
    if membership is None:
        raise ForbiddenError("You are not a member of this project.")
    return membership


def assert_maintainer(membership: ProjectMember) -> None:
    if membership.role != ProjectRole.MAINTAINER.value:
        raise ForbiddenError("Only project maintainers can perform this action.")
