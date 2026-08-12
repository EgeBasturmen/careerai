from fastapi import HTTPException, status

from sqlalchemy.orm import Session

from src.core.security.jwt import create_access_token
from src.core.security.password import hash_password, verify_password
from src.domains.users.repositories.user_repository import UserRepository
from src.domains.users.schemas.user_schema import (
    TokenResponse,
    UserCreateRequest,
    UserLoginRequest,
    UserResponse,
)


class UserService:
    def __init__(
        self,
        db: Session,
    ):
        self.repository = UserRepository(db)

    def register(
        self,
        request: UserCreateRequest,
    ) -> UserResponse:
        existing_user = self.repository.get_by_email(
            request.email,
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        hashed_password = hash_password(
            request.password,
        )

        user = self.repository.create(
            email=request.email,
            hashed_password=hashed_password,
            full_name=request.full_name,
        )

        return UserResponse.model_validate(user)

    def login(
        self,
        request: UserLoginRequest,
    ) -> TokenResponse:
        user = self.repository.get_by_email(
            request.email,
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        is_valid_password = verify_password(
            request.password,
            user.hashed_password,
        )

        if not is_valid_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        token = create_access_token(
            subject=str(user.id),
        )

        return TokenResponse(
            access_token=token,
        )