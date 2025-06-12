from fastapi import FastAPI
from home_budget.apps.user.routes import router as user_router
from home_budget.apps.category.routes import router as categories_router
from home_budget.apps.expense.routes import router as expense_router

app = FastAPI()
app.include_router(user_router, prefix="/api/v1/users", tags=["users"])
app.include_router(categories_router, prefix="/api/v1/categories", tags=["categories"])
app.include_router(expense_router, prefix="/api/v1/expenses", tags=["expenses"])

