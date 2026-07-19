from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db import get_db
from app.models.user import User
from app.schemas.project import MemberAdd, MemberOut, ProjectCreate, ProjectOut
from app.schemas.user import UserOut
from app.services import authz, project_service

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.post("", response_model=ProjectOut, status_code=201)
def create_project(
    payload: ProjectCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> ProjectOut:
    project = project_service.create_project(
        db, owner=user, name=payload.name, key=payload.key, description=payload.description
    )
    return ProjectOut(
        id=project.id,
        name=project.name,
        key=project.key,
        description=project.description,
        created_at=project.created_at,
        role="maintainer",
    )


@router.get("", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[ProjectOut]:
    rows = project_service.list_projects_for_user(db, user.id)
    return [
        ProjectOut(
            id=project.id,
            name=project.name,
            key=project.key,
            description=project.description,
            created_at=project.created_at,
            role=membership.role,
        )
        for project, membership in rows
    ]


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> ProjectOut:
    membership = authz.get_membership_or_403(db, project_id=project_id, user_id=user.id)
    project = authz.get_project_or_404(db, project_id)
    return ProjectOut(
        id=project.id,
        name=project.name,
        key=project.key,
        description=project.description,
        created_at=project.created_at,
        role=membership.role,
    )


@router.post("/{project_id}/members", response_model=MemberOut, status_code=201)
def add_member(
    project_id: int,
    payload: MemberAdd,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MemberOut:
    membership, target_user = project_service.add_member(
        db, project_id=project_id, requester=user, email=payload.email, role=payload.role
    )
    return MemberOut(role=membership.role, user=UserOut.model_validate(target_user))


@router.get("/{project_id}/members", response_model=list[MemberOut])
def list_members(
    project_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> list[MemberOut]:
    rows = project_service.list_members(db, project_id=project_id, requester=user)
    return [MemberOut(role=membership.role, user=UserOut.model_validate(u)) for membership, u in rows]
