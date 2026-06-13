from pydantic import BaseModel


# Erstelle Rezept ohne ID (macht DB)
class RecipeCreate(BaseModel):
    title: str
    description: str
    instructions: str


class RecipeResponse(BaseModel):
    id: int
    title: str
    description: str
    ingredients: str
    instructions: str

    class Config:
        from_attributes = True  # Um SQLAlchemy Sachen zu konvertieren
