from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database.db import get_db
from models.user import User, UserUpdate, UserPasswordChange, UserResponse
from services.user_service import UserService
from utils.security import get_current_active_user
from utils.helpers import api_response

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/profile", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_active_user)):
    """Retrieve current user profile."""
    return current_user


@router.put("/profile", response_model=UserResponse)
def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update profile details (name, email)."""
    updated_user = UserService.update_profile(db, current_user, user_update)
    return updated_user


@router.post("/change-password")
def change_password(
    pwd_change: UserPasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change current user account password."""
    UserService.change_password(db, current_user, pwd_change)
    return {"success": True, "message": "Password changed successfully"}
