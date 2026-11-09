
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.dependencies import (
    get_db,
    get_current_user,
    get_current_admin
)

router = APIRouter(prefix="/users", tags=["Users"])


# ==========================================
# 1. Get Current User Profile
# ==========================================
@router.get("/me", response_model=schemas.UserResponse)
def get_my_profile(
    current_user: models.User = Depends(get_current_user)
):
    return current_user


# ==========================================
# 2. Get All Users (Admin Only)
# ==========================================
@router.get("/admin/all", response_model=list[schemas.UserResponse])
def get_all_users(
    current_admin: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    users = db.query(models.User).all()
    return users


# ==========================================
# 3. Get Single User (Admin Only)
# ==========================================
@router.get("/{user_id}", response_model=schemas.UserResponse)
def get_user(
    user_id: int,
    current_admin: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


# ==========================================
# 4. Update User (Admin Only)
# ==========================================
@router.put("/{user_id}", response_model=schemas.UserResponse)
def update_user(
    user_id: int,
    user_data: schemas.UserUpdate,
    current_admin: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    update_data = user_data.model_dump(exclude_unset=True)

    if "email" in update_data:
        existing_user = db.query(models.User).filter(
            models.User.email == update_data["email"],
            models.User.id != user_id
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )

    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)

    return user


# ==========================================
# 5. Delete User (Admin Only)
# ==========================================
@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    current_admin: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin cannot delete their own account"
        )

    db.delete(user)
    db.commit()

    return {
        "message": "User deleted successfully",
        "user_id": user_id
    }
