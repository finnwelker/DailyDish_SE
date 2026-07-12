from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import datetime
from database import Base


class SuggestionHistory(Base):
    __tablename__ = "suggestion_history"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    recipe_id = Column(Integer, ForeignKey("recipes.id"))
    suggestion_time = Column(DateTime, default=datetime.datetime.utcnow)

    recipe = relationship("Recipe")
