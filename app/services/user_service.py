from sqlalchemy.orm import Session

from app import schemas
from app.core.security import hash_password
from app.repositories import user_repository


def get_user_profile(db: Session, user_id: int):
    return user_repository.get_user_by_id(db, user_id)


def get_user_by_email(db: Session, email: str):
    return user_repository.get_user_by_email(db, email)


def get_all_users(db: Session):
    return user_repository.get_all_users(db)


def register_user(db: Session, user_data: schemas.UserRegister):

    # Check existing email
    existing_user = user_repository.get_user_by_email(
        db,
        user_data.email
    )

    if existing_user:
        return None

    # Convert schema to dictionary
    user_dict = user_data.model_dump(
        exclude={"password"}
    )

    # Hash password
    user_dict["password_hash"] = hash_password(
        user_data.password
    )

    # Create user
    return user_repository.create_user(
        db,
        user_dict
    )