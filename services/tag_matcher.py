from sqlalchemy.orm import Session
from models.recipe import Recipe
from models.user import User


# Wir berechnen den Score aus zwei Sets mit Jaccard-Koeffizient
def calculate_score(user_tags: set, recipe_tags: set) -> float:
    if not user_tags or not recipe_tags:
        return 0.0

    intersection = user_tags & recipe_tags
    union = user_tags | recipe_tags

    return len(intersection) / len(union) # Der Jaccard-Koeffizient (ist einfach die absoluten Werte der Schnitt- und Vereinigungsmenge dividiert)


def get_suggestion(user_id: int, db: Session):
    # Wir holen den User mit der ID
    user = db.query(User).filter(User.id == user_id).first()

    # TODO: Später mit Exception
    if not user:
        return None

    required_tags = {tag.name for tag in user.tags if tag.is_required}
    preference_tags = {tag.name for tag in user.tags if not tag.is_required}

    # Und alle Rezepte
    recipes = db.query(Recipe).all()

    valid_recipes = []
    for recipe in recipes:
        recipe_tags = {tag.name for tag in recipe.tags}
        if required_tags.issubset(recipe_tags):
            valid_recipes.append(recipe)

    best_recipe = None
    best_score = -1

    for recipe in valid_recipes:
        recipe_tags = {tag.name for tag in recipe.tags}
        score = calculate_score(preference_tags, recipe_tags)

        if score > best_score:
            best_score = score
            best_recipe = recipe

    return best_recipe
