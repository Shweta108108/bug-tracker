from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.user import User


def create(db: Session, *, name: str, key: str, description: str | None) -> Project:
    project = Project(name=name, key=key, description=description)
    db.add(project)
    db.flush()
    return project


def get_by_id(db: Session, project_id: int) -> Project | None:
    return db.get(Project, project_id)


def get_by_key(db: Session, key: str) -> Project | None:
    return db.scalar(select(Project).where(Project.key == key))


def get_membership(db: Session, *, project_id: int, user_id: int) -> ProjectMember | None:
    return db.get(ProjectMember, {"project_id": project_id, "user_id": user_id})


def add_membership(db: Session, *, project_id: int, user_id: int, role: str) -> ProjectMember:
    member = ProjectMember(project_id=project_id, user_id=user_id, role=role)
    db.add(member)
    db.flush()
    return member


def list_for_user(db: Session, user_id: int) -> list[tuple[Project, ProjectMember]]:
    stmt = (
        select(Project, ProjectMember)
        .join(ProjectMember, ProjectMember.project_id == Project.id)
        .where(ProjectMember.user_id == user_id)
        .order_by(Project.created_at.desc())
    )
    return list(db.execute(stmt).all())


def list_members(db: Session, project_id: int) -> list[tuple[ProjectMember, User]]:
    stmt = (
        select(ProjectMember, User)
        .join(User, User.id == ProjectMember.user_id)
        .where(ProjectMember.project_id == project_id)
        .order_by(User.name)
    )
    return list(db.execute(stmt).all())
