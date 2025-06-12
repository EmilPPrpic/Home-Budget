from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from home_budget.db import get_session
from .auth_utils import create_access_token
from .models import User
from .schemas import UserCreate, UserResponse, Token
from ..category.utils import create_predefined_categories

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_session)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    new_user = User(username=user.username, password=pwd_context.hash(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    create_predefined_categories(db, new_user.id)
    return UserResponse(id=new_user.id, username=new_user.username)


@router.post("/login", response_model=Token)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_session)):
    db_user = db.query(User).filter(User.username == form_data.username).first()

    if not db_user or not pwd_context.verify(form_data.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": db_user.username})
    return Token(access_token=token)


@router.delete("/{username}", response_model=UserResponse)
async def delete_user(username: str, db: Session = Depends(get_session)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return UserResponse(id=user.id, username=user.username)
