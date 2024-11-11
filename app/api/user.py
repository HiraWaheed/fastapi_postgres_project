import jwt
import logging
from app.utils.helper import (
    SECRET_KEY,
    hash_password,
    verify_password,
    create_access_token,
)
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.constants import ALGORITHM
import app.models.user as UserModel
from app.database import get_db
import app.schemas.user as UserSchema


router = APIRouter()


@router.post("/user", response_model=UserSchema.UserCreateResponse | str)
def register_user(user_data: UserSchema.UserCreate, db: Session = Depends(get_db)):
    try:
        # Check if username already exists
        existing_user = (
            db.query(UserModel.User)
            .filter(UserModel.User.username == user_data.username)
            .first()
        )
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Username already exists. Please enter a different username",
            )

        # Hash the password before saving
        hashed_password = hash_password(user_data.password)
        new_user = UserModel.User(username=user_data.username, password=hashed_password)

        # Add new user to the database
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user
    except HTTPException as e:
        logging.error(f"HTTPException occurred at register_user: {e.detail}")
        raise e  # Re-raise the HTTPException with the correct status code and detail
    except Exception as e:
        logging.error(f"Something went wrong: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong.",
        )


@router.post("/login", response_model=UserSchema.UserToken | str)
def login(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    try:
        user = (
            db.query(UserModel.User)
            .filter(UserModel.User.username == form_data.username)
            .first()
        )
        if not user or not verify_password(form_data.password, user.password):
            raise HTTPException(status_code=400, detail="Invalid credentials")

        # Create and return the access token
        access_token = create_access_token(data={"username": user.username})
        return UserSchema.UserToken(access_token=access_token, token_type="bearer")

    except HTTPException as e:
        logging.error(f"HTTPException occurred at register_user: {e.detail}")
        raise e  # Re-raise the HTTPException with the correct status code and detail
    except Exception as e:
        logging.error(f"Something went wrong: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong.",
        )


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": True}
        )
        username: str = payload.get("username")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = (
            db.query(UserModel.User).filter(UserModel.User.username == username).first()
        )
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid user")
        return user

    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token {e}")


@router.get("/me", response_model=UserSchema.UserCreateResponse)
def get_me(current_user: UserModel = Depends(get_current_user)):
    return current_user
