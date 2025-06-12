from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from home_budget.apps.user.auth_utils import get_current_user
from home_budget.apps.user.models import User
from home_budget.db import get_session
from .models import Expense
from .schemas import ExpenseCreate, ExpenseResponse, ExpenseUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter()


@router.post("/create", response_model=ExpenseResponse)
async def create_expense(expense: ExpenseCreate, db: Session = Depends(get_session),
                         current_user: User = Depends(get_current_user)):
    if db.query(Expense).filter(Expense.name == expense.name, Expense.user_id == current_user.id).first():
        raise HTTPException(
            status_code=400,
            detail="Category already exists"
        )
    new_expense = Expense(**expense.dict(), user_id=current_user.id)
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return new_expense


@router.get("/getAll", response_model=list[ExpenseResponse])
async def get_all_expenses(db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    return db.query(Expense).filter(Expense.user_id == current_user.id).all()


@router.get("/getByCategory/{category_id}", response_model=list[ExpenseResponse])
async def get_all_expenses_by_category(category_id: int, db: Session = Depends(get_session),
                                       current_user: User = Depends(get_current_user)):
    expenses = db.query(Expense).filter(Expense.category_id == category_id, Expense.user_id == current_user.id).all()
    if not expenses:
        raise HTTPException(status_code=404, detail="No expenses found for this category")
    return expenses


@router.put("/update/{expense_id}", response_model=ExpenseResponse)
async def update_expense(expense_id: int, expense_update: ExpenseUpdate, db: Session = Depends(get_session),
                         current_user: User = Depends(get_current_user)):
    expense = db.query(Expense).filter(Expense.id == expense_id, Expense.user_id == current_user.id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    for key, value in expense_update.dict(exclude_unset=True).items():
        setattr(expense, key, value)

    db.commit()
    db.refresh(expense)
    return expense


@router.delete("/delete/{expense_id}", status_code=200)
async def delete_expense(expense_id: int, db: Session = Depends(get_session),
                         current_user: User = Depends(get_current_user)):
    expense = db.query(Expense).filter(Expense.id == expense_id, Expense.user_id == current_user.id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    db.delete(expense)
    db.commit()
    return {"detail": "Expense deleted successfully"}


@router.get("/summary")
async def get_expenses_summary(
        start_date: date = Query(...),
        end_date: date = Query(...),
        db: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Start date must be before end date")

    expenses = db.query(Expense).filter(
        Expense.user_id == current_user.id,
        Expense.date >= start_date,
        Expense.date <= end_date
    ).all()

    if not expenses:
        raise HTTPException(status_code=404, detail="No expenses found for the given date range")

    category_performance = {}

    for expense in expenses:
        cid = expense.category_id
        if cid not in category_performance:
            category_performance[cid] = {
                "category_id": cid,
                "total_expenses": 0,
                "highest_expense": expense.amount,
                "lowest_expense": expense.amount,
                "count": 0
            }

        cat = category_performance[cid]
        cat["total_expenses"] += expense.amount
        cat["count"] += 1
        cat["highest_expense"] = max(cat["highest_expense"], expense.amount)
        cat["lowest_expense"] = min(cat["lowest_expense"], expense.amount)

    for cat in category_performance.values():
        cat["average_expense"] = round(cat["total_expenses"] / cat["count"], 2)

    return {
        "total_expenses": round(sum(exp.amount for exp in expenses), 2),
        "category_performance": list(category_performance.values())
    }
