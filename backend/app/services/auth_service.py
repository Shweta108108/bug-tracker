from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import create_access_token, hash_password, verify_password
from app.dao import user_dao
from app.models.user import User


def signup(db: Session, *, name: str, email: str, password: str) -> User:
    if user_dao.get_by_email(db, email) is not None:
        raise ConflictError("An account with this email already exists.", details={"field": "email"})
    user = user_dao.create(db, name=name, email=email, password_hash=hash_password(password))
    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, *, email: str, password: str) -> str:
    user = user_dao.get_by_email(db, email)
    if user is None or not verify_password(password, user.password_hash):
        raise UnauthorizedError("Invalid email or password.")
    return create_access_token(user.id)
