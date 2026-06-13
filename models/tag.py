from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base


class Tag(Base):
    __tablename__ = "tags"

    # Erstelle die Tabelle für unsere Tags, bestehend aus ID, Name und in welchen Rezepten das Tag vorhanden ist
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    recipes = relationship("Recipe", secondary="recipe_tags", back_populates="tags")



