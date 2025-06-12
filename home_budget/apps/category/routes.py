from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from home_budget.apps.user.auth_utils import get_current_user
from home_budget.apps.user.models import User
from home_budget.db import get_session
from .models import Category
from .schemas import CategoryCreate, CategoryResponse, CategoryUpdate

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
    return db.query(Category).filter(Category.user_id == current_user.id).all()


@router.put("/update/{category_id}", response_model=CategoryResponse)
async def update_category(category_id: int, category_update: CategoryUpdate, db: Session = Depends(get_session),
                          current_user: User = Depends(get_current_user)):
    category = db.query(Category).filter(Category.id == category_id, Category.user_id == current_user.id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    for key, value in category_update.dict(exclude_unset=True).items():
        setattr(category, key, value)

    db.commit()
    db.refresh(category)
    return category


@router.delete("/delete/{category_id}", status_code=200)
async def delete_category(category_id: int, db: Session = Depends(get_session),
                          current_user: User = Depends(get_current_user)):
    category = db.query(Category).filter(Category.id == category_id, Category.user_id == current_user.id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    db.delete(category)
    db.commit()
    return {"detail": "Category deleted successfully"}
