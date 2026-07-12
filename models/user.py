from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from models.suggestion_history import SuggestionHistory

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    tags = relationship("Tag", secondary="user_tags")
    favourite_recipes = relationship("Recipe", secondary="favourites")
    suggestion_history = relationship("SuggestionHistory")
