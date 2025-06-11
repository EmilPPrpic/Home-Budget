from typing import Annotated

from db import get_session
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .models import User
from .schemas import UserCreate, UserResponse, UserLogin, Token
from .security_utils import create_access_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter()


# register
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
    return UserResponse(id=new_user.id, username=new_user.username)


@router.post("/login", response_model=Token)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_session)):
    db_user = db.query(User).filter(User.username == form_data.username).first()
    print(db_user)

    if not db_user or not pwd_context.verify(form_data.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": db_user.username})
    return Token(access_token=token)

