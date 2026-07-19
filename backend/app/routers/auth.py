from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.auth import LoginRequest, SignupRequest, TokenResponse
from app.schemas.user import UserOut
from app.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/signup", response_model=UserOut, status_code=201)
def signup(payload: SignupRequest, db: Session = Depends(get_db)) -> UserOut:
    user = auth_service.signup(db, name=payload.name, email=payload.email, password=payload.password)
    return UserOut.model_validate(user)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    token = auth_service.authenticate(db, email=payload.email, password=payload.password)
    return TokenResponse(access_token=token)


@router.post("/logout", status_code=204)
def logout() -> None:
    # Stateless JWT: nothing to invalidate server-side. Logout is a client-side
    # token discard; this endpoint exists only for API symmetry with the spec.
    return None
