import smtplib

from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from database import get_db
from src.dto.user import UserUpdate, UserModel, UserForgotPassword
from src.models.user import User
from src.services.profile import get_current_user, generate_random_password, send_password_email

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()


@router.get("/profile/user/", response_model=UserModel)
async def get_user_by_token(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/profile/edit/")
async def update_user_profile(
    profile_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not any(vars(profile_data).values()):
        raise HTTPException(status_code=400, detail="No data provided")
    user = db.query(User).filter(User.id == current_user.id).first()
    if user:
        if profile_data.username:
            user.username = profile_data.username
        if profile_data.phone_number:
            user.phone_number = profile_data.phone_number
        if profile_data.password and profile_data.new_password:
            if pwd_context.verify(profile_data.password, user.password):
                user.password = pwd_context.hash(profile_data.new_password)
            else:
                raise HTTPException(status_code=400, detail="Invalid old password")
        elif profile_data.password and not profile_data.new_password:
            raise HTTPException(status_code=400, detail="Type new password!")
        elif not profile_data.password and profile_data.new_password:
            raise HTTPException(status_code=400, detail="Type old password!")
        db.commit()
        db.refresh(user)
        return {"message": "User updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")


@router.post("/profile/password/")
async def remind_user_password(
        user_data: UserForgotPassword,
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == user_data.email).first()
    if user:
        new_password = generate_random_password()
        hashed_password = pwd_context.hash(new_password)

        try:
            send_password_email(user.email, new_password)
        except smtplib.SMTPException as e:
            raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

        user.password = hashed_password
        db.commit()

        return {"message": "Password reminder sent successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")


