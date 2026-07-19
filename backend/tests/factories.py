import itertools

from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password
from app.models.comment import Comment
from app.models.enums import IssuePriority, IssueStatus, ProjectRole
from app.models.issue import Issue
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.user import User

_counter = itertools.count(1)


def create_user(db: Session, *, name: str | None = None, email: str | None = None, password: str = "password123") -> User:
    n = next(_counter)
    user = User(
        name=name or f"User {n}",
        email=email or f"user{n}@example.com",
        password_hash=hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_project(db: Session, *, owner: User, name: str | None = None, key: str | None = None) -> Project:
    n = next(_counter)
    project = Project(name=name or f"Project {n}", key=key or f"P{n}", description="test project")
    db.add(project)
    db.flush()
    db.add(ProjectMember(project_id=project.id, user_id=owner.id, role=ProjectRole.MAINTAINER.value))
    db.commit()
    db.refresh(project)
    return project


def add_member(db: Session, *, project: Project, user: User, role: str = ProjectRole.MEMBER.value) -> ProjectMember:
    member = ProjectMember(project_id=project.id, user_id=user.id, role=role)
    db.add(member)
    db.commit()
    return member


def create_issue(
    db: Session,
    *,
    project: Project,
    reporter: User,
    title: str | None = None,
    status: str = IssueStatus.OPEN.value,
    priority: str = IssuePriority.MEDIUM.value,
    assignee: User | None = None,
) -> Issue:
    n = next(_counter)
    issue = Issue(
        project_id=project.id,
        title=title or f"Issue {n}",
        description="test issue",
        status=status,
        priority=priority,
        reporter_id=reporter.id,
        assignee_id=assignee.id if assignee else None,
    )
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue


def create_comment(db: Session, *, issue: Issue, author: User, body: str = "test comment") -> Comment:
    comment = Comment(issue_id=issue.id, author_id=author.id, body=body)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def auth_headers(user: User) -> dict[str, str]:
    token = create_access_token(user.id)
    return {"Authorization": f"Bearer {token}"}
