from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.recipe import Recipe
from schemas.recipeSchem import RecipeResponse

router = APIRouter(prefix="/user", tags=["Favourites"])

@router.post("/{user_id}/favourites/{recipe_id}", response_model=RecipeResponse)
def add_favourite(user_id: int, recipe_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User nicht gefunden")

    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Rezept nicht gefunden")

    if recipe in user.favourite_recipes:
        raise HTTPException(status_code=400, detail="Rezept bereits in Favoriten")

    user.favourite_recipes.append(recipe)
    db.commit()
    return recipe


@router.get("/{user_id}/favourites", response_model=list[RecipeResponse])
def get_favourites(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User nicht gefunden")

    return user.favourite_recipes


@router.delete("/{user_id}/favourites/{recipe_id}")
def remove_favourite(user_id: int, recipe_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User nicht gefunden")

    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Rezept nicht gefunden")

    if recipe not in user.favourite_recipes:
        raise HTTPException(status_code=400, detail="Rezept nicht in Favoriten")

    user.favourite_recipes.remove(recipe)
    db.commit()
    return {"detail": "Favorit entfernt"}