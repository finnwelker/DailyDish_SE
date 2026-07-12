from sqlalchemy.orm import Session
from models.recipe import Recipe
from models.user import User
from models.suggestion_history import SuggestionHistory

import datetime

COOLDOWN_HOURS = 24
HISTORY_DAYS = 7


# Wir berechnen den Score aus zwei Sets mit Jaccard-Koeffizient
def calculate_score(user_tags: set, recipe_tags: set) -> float:
    if not user_tags or not recipe_tags:
        return 0.0

    intersection = user_tags & recipe_tags
    union = user_tags | recipe_tags

    return len(intersection) / len(union) # Der Jaccard-Koeffizient (ist einfach die absoluten Werte der Schnitt- und Vereinigungsmenge dividiert)


def empty_old_history(user: User, db: Session):
    # Wir löschen Einträge die älter als 7 Tage sind
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=HISTORY_DAYS)
    for entry in user.suggestion_history:
        if entry.suggestion_time < cutoff:
            db.delete(entry)
    db.commit()


def get_last_suggestion(user:User):
    # Gibt den letzten Eintrag im Verlauf zurück
    if not user.suggestion_history:
        return None
    return max(user.suggestion_history, key=lambda x: x.suggestion_time)


def find_best_recipe(user: User, db: Session, skip_id: int | None = None):
    # MIt Jaccard das beste noch nicht gesehene Rezept auswählen
    seen_ids = {entry.recipe_id for entry in user.suggestion_history}

    # Bei Skip aktuelles Rezept ausschließen
    if skip_id:
        seen_ids.add(skip_id)

    required_tags = {tag.name for tag in user.tags if tag.is_required}
    preference_tags = {tag.name for tag in user.tags if not tag.is_required}

    recipes = db.query(Recipe).all()

    # Pflicht-Tags filtern + bereits gesehene ausschließen
    valid_recipes = [
        r for r in recipes
        if r.id not in seen_ids
        and required_tags.issubset({tag.name for tag in r.tags})
    ]

    # Alle gesehen → History zurücksetzen
    if not valid_recipes:
        user.suggestion_history.clear()
        db.commit()
        valid_recipes = [
            r for r in recipes
            if r.id != skip_id
            if required_tags.issubset({tag.name for tag in r.tags})
        ]

    if not valid_recipes:
        return None

    # Bestes Rezept per Jaccard
    return max(
        valid_recipes,
        key=lambda r: calculate_score(preference_tags, {tag.name for tag in r.tags})
    )


def get_suggestion(user_id: int, db: Session, skip: bool = False):
    # Wir holen den User mit der ID
    user = db.query(User).filter(User.id == user_id).first()

    # TODO: Später mit Exception
    if not user:
        return None

    empty_old_history(user, db)
    db.refresh(user)

    last = get_last_suggestion(user)
    now = datetime.datetime.utcnow()

    # Falls noch kein neuer Tag und Skip nicht gewählt wurde
    if last and not skip:
        hours_since = (now - last.suggestion_time).total_seconds()/3600
        if hours_since < COOLDOWN_HOURS:
            return last.recipe

    # Neues Rezept suchen oder bei skip letztes ausschließen
    skip_id = last.recipe_id if (last and skip) else None
    best_recipe = find_best_recipe(user, db, skip_id=skip_id)

    if best_recipe:
        entry = SuggestionHistory(
            user_id=user.id,
            recipe_id=best_recipe.id,
            suggestion_time=now
        )
        db.add(entry)
        db.commit()

    return best_recipe
