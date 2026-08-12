from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from src.core.database.session import get_db
from src.core.security.dependencies import get_current_user
from src.domains.users.models.user import User
from src.domains.users.schemas.user_schema import (
    TokenResponse,
    UserCreateRequest,
    UserLoginRequest,
    UserResponse,
)
from src.domains.users.services.user_service import UserService
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post(
    "/register",
    response_model=UserResponse,
)
def register(
    request: UserCreateRequest,
    db: Session = Depends(get_db),
):
    service = UserService(db)

    return service.register(request)


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    service = UserService(db)

    request = UserLoginRequest(
        email=form_data.username,
        password=form_data.password,
    )

    return service.login(request)

@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user