from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint

from home_budget.db import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))

    __table_args__ = (
        UniqueConstraint('name', 'user_id', name='unique_category_per_user'),
    )
