from typing import Optional

from pydantic import BaseModel


class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]

    class Config:
        orm_mode = True


class CategoryUpdate(BaseModel):
    id: int
    name: Optional[str] = None
    description: Optional[str] = None
