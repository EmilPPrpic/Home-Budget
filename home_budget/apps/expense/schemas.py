from datetime import date
from typing import Optional

from pydantic import BaseModel


class ExpenseCreate(BaseModel):
    name: str
    description: Optional[str] = None
    amount: int
    date: date
    category_id: int


class ExpenseResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    amount: int
    date: date
    category_id: int

    class Config:
        orm_mode = True


class ExpenseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[int] = None
    date: Optional[date] = None
    category_id: Optional[int] = None


class CategoryPerformance(BaseModel):
    category_id: int
    total_expenses: int
    average_expense: float
    highest_expense: int
    lowest_expense: int

    class Config:
        orm_mode = True


class ExpenseSummaryResponse(BaseModel):
    total_expenses: float
    category_performance: list[CategoryPerformance]
