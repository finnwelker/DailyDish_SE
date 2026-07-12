from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas.recipeSchem import RecipeResponse
from services.tag_matcher import get_suggestion

router = APIRouter(prefix="/suggestions", tags=["Suggestions"])


@router.get("/{user_id}", response_model=RecipeResponse)
def suggest_recipe(user_id: int, db: Session = Depends(get_db)):
    recipe = get_suggestion(user_id, db)

    if not recipe:
        raise HTTPException(status_code=404, detail="Kein passendes Rezept gefunden")

    return {
        "id": recipe.id,
        "title": recipe.title,
        "description": recipe.description,
        "ingredients": recipe.ingredients,
        "instructions": recipe.instructions,
        "tags": [tag.name for tag in recipe.tags],
    }
