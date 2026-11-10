from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas
from app.dependencies import (
    get_db,
    get_current_user,
    get_current_admin
)
from app.services import user_service


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# Get current user's profile
@router.get(
    "/me",
    response_model=schemas.UserResponse
)
def get_my_profile(
    current_user: models.User = Depends(get_current_user)
):
    return current_user


# Get all users (Admin only)
@router.get(
    "/",
    response_model=list[schemas.UserResponse]
)
def get_all_users(
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin)
):
    return user_service.get_all_users(db)