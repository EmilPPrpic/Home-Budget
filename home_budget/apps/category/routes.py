from apps.user.models import User
from apps.user.security_utils import get_current_user
from db import get_session
from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .models import Category
from .schemas import CategoryCreate, CategoryResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter()


@router.post("/create", response_model=CategoryResponse)
async def create_category(category: CategoryCreate, db: Session = Depends(get_session),
                          current_user: User = Depends(get_current_user)):
    if db.query(Category).filter(Category.name == category.name, Category.user_id == current_user.id).first():
        raise HTTPException(
            status_code=400,
            detail="Category already exists"
        )
    new_category = Category(**category.dict(), user_id=current_user.id)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category


@router.get("/getAll", response_model=list[CategoryResponse])
async def get_all_categories(db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    categories = db.query(Category).filter(Category.user_id == current_user.id).all()
    return categories
