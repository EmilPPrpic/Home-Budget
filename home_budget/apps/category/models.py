from sqlalchemy import Column, Integer, String, ForeignKey

from db import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    # TODO: add icon field


