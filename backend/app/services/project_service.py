from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.dao import project_dao, user_dao
from app.models.enums import ProjectRole
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.user import User
from app.services import authz


def create_project(db: Session, *, owner: User, name: str, key: str, description: str | None) -> Project:
    if project_dao.get_by_key(db, key) is not None:
        raise ConflictError("A project with this key already exists.", details={"field": "key"})
    project = project_dao.create(db, name=name, key=key, description=description)
    project_dao.add_membership(db, project_id=project.id, user_id=owner.id, role=ProjectRole.MAINTAINER.value)
    db.commit()
    db.refresh(project)
    return project


def list_projects_for_user(db: Session, user_id: int) -> list[tuple[Project, ProjectMember]]:
    return project_dao.list_for_user(db, user_id)


def add_member(db: Session, *, project_id: int, requester: User, email: str, role: str) -> tuple[ProjectMember, User]:
    membership = authz.get_membership_or_403(db, project_id=project_id, user_id=requester.id)
    authz.assert_maintainer(membership)

    target_user = user_dao.get_by_email(db, email)
    if target_user is None:
        raise NotFoundError(
            "No account exists for this email.", details={"field": "email"}, code="USER_NOT_FOUND"
        )

    if project_dao.get_membership(db, project_id=project_id, user_id=target_user.id) is not None:
        raise ConflictError("This user is already a member of the project.", code="ALREADY_MEMBER")

    new_membership = project_dao.add_membership(db, project_id=project_id, user_id=target_user.id, role=role)
    db.commit()
    db.refresh(new_membership)
    return new_membership, target_user


def list_members(db: Session, *, project_id: int, requester: User) -> list[tuple[ProjectMember, User]]:
    authz.get_membership_or_403(db, project_id=project_id, user_id=requester.id)
    return project_dao.list_members(db, project_id)
