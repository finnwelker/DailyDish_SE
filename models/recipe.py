from sqlalchemy import Column, Integer, String, Table, ForeignKey
from database import Base
from sqlalchemy.orm import relationship


class Recipe(Base):
    __tablename__ = "recipes"

    # Erstelle die Tabelle für unsere Rezepte, bestehend aus ID, Name, Beschreibung, Anweisungen und welche Tags das Rezept enthält
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    ingredients = Column(String, nullable=False)
    instructions = Column(String)

    tags = relationship("Tag", secondary="recipe_tags", back_populates="recipes")

