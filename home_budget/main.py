from fastapi import FastAPI
from apps.user.routes import router as user_router
from apps.category.routes import router as categories_router

from db import get_session

app = FastAPI()
app.include_router(user_router, prefix="/api/v1/users", tags=["users"])
app.include_router(categories_router, prefix="/api/v1/categories", tags=["categories"])
session = get_session()

