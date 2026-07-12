import datetime
from unittest.mock import MagicMock
from services.tag_matcher import (
    calculate_score,
    find_best_recipe,
    get_last_suggestion,
    get_suggestion,
    empty_old_history,
    COOLDOWN_HOURS,
    HISTORY_DAYS
)

# Alle Modelle importieren damit SQLAlchemy die Mapper konfigurieren kann
import models.join_tables
import models.tag
from models.user import User
from models.recipe import Recipe


# Disclaimer Tests teilweise mit KI (Claude) generiert


# Hilfsfunktionen
def make_tag(name, is_required=False):
    tag = MagicMock()
    tag.name = name
    tag.is_required = is_required
    return tag


def make_recipe(title, tag_names, recipe_id=None):
    recipe = MagicMock()
    recipe.id = recipe_id or hash(title)
    recipe.title = title
    recipe.tags = [make_tag(n) for n in tag_names]
    return recipe


def make_history_entry(recipe, hours_ago=0):
    entry = MagicMock()
    entry.recipe_id = recipe.id
    entry.recipe = recipe
    entry.suggestion_time = datetime.datetime.utcnow() - datetime.timedelta(hours=hours_ago)
    return entry


def make_user(preference_tags=None, required_tags=None, history_entries=None):
    user = MagicMock()
    user.id = 1
    all_tags = []
    for name in (preference_tags or []):
        all_tags.append(make_tag(name, is_required=False))
    for name in (required_tags or []):
        all_tags.append(make_tag(name, is_required=True))
    user.tags = all_tags
    user.suggestion_history = history_entries or []
    return user


# calculate_score Tests
def test_score_best_case():
    assert calculate_score({"vegan", "asiatisch"}, {"vegan", "asiatisch"}) == 1.0


def test_score_worst_case():
    assert calculate_score({"vegan", "asiatisch"}, {"vegetarisch", "italienisch"}) == 0.0


def test_score_mixed_result():
    score = calculate_score({"vegan"}, {"vegan", "italienisch", "schnell"})
    assert round(score, 2) == .33


def test_empty_user_tags():
    assert calculate_score(set(), {"vegan", "italienisch"}) == 0.0


def test_empty_recipe_tags():
    assert calculate_score({"vegan"}, set()) == 0.0


def test_both_empty():
    assert calculate_score(set(), set()) == 0.0


def test_score_returns_float():
    result = calculate_score({"vegan"}, {"vegan"})
    assert isinstance(result, float)


# get_last_suggestion Tests
def test_last_suggestion_empty():
    user = make_user()
    assert get_last_suggestion(user) is None


def test_last_suggestion_one_entry():
    user = make_user()
    recipe = make_recipe("Curry", ["asiatisch"], recipe_id=1)
    entry = make_history_entry(recipe, hours_ago=5)
    user = make_user(history_entries=[entry])
    assert get_last_suggestion(user) == entry


def test_last_suggestion_multiple_entries():
    user = make_user()
    recipe1 = make_recipe("Curry", ["asiatisch"], recipe_id=1)
    recipe2 = make_recipe("Bolognese", ["italienisch"], recipe_id=2)
    old = make_history_entry(recipe1, hours_ago=10)
    new = make_history_entry(recipe2, hours_ago=2)
    user = make_user(history_entries=[old, new])

    assert get_last_suggestion(user) == new


# find_best_recipe Tests
def test_best_recipe():
    db = MagicMock()
    curry = make_recipe("Curry", ["asiatisch", "vegan", "vegetarisch"], recipe_id=1)
    pasta = make_recipe("Pasta", ["italienisch"], recipe_id=2)
    db.query().all.return_value = [curry, pasta]
    user = make_user(preference_tags=["asiatisch", "schnell"])

    result = find_best_recipe(user, db)
    assert result.title == "Curry"


def test_already_seen_recipes_excluded():
    db = MagicMock()
    curry = make_recipe("Curry", ["asiatisch"], recipe_id=1)
    pasta = make_recipe("Pasta", ["asiatisch"], recipe_id=2)

    entry = make_history_entry(curry)
    user = make_user(preference_tags=["asiatisch"], history_entries=[entry])
    db.query().all.return_value = [curry, pasta]

    result = find_best_recipe(user, db)
    assert result.title == "Pasta"


def test_skip_id_excludes_recipe():
    db = MagicMock()
    curry = make_recipe("Curry", ["asiatisch"], recipe_id=1)
    pasta = make_recipe("Pasta", ["asiatisch"], recipe_id=2)
    db.query().all.return_value = [curry, pasta]
    user = make_user(preference_tags=["asiatisch"])

    result = find_best_recipe(user, db, skip_id=1)
    assert result.title == "Pasta"


def test_mandatory_tag_prohibits_recipe():
    db = MagicMock()
    fleisch = make_recipe("Schnitzel", ["deutsch"], recipe_id=1)
    curry = make_recipe("Curry", ["vegetarisch", "asiatisch"], recipe_id=2)
    db.query().all.return_value = [fleisch, curry]
    user = make_user(preference_tags=["asiatisch"], required_tags=["vegetarisch"])

    result = find_best_recipe(user, db)
    assert result.title == "Curry"


def test_all_recipes_seen_reset():
    db = MagicMock()
    curry = make_recipe("Curry", ["asiatisch"], recipe_id=1)
    entry = make_history_entry(curry)
    user = make_user(preference_tags=["asiatisch"], history_entries=[entry])
    db.query().all.return_value = [curry]

    result = find_best_recipe(user, db)
    # Nach Reset soll Curry wieder vorgeschlagen werden
    assert result.title == "Curry"
    # History soll gecleart worden sein
    assert len(user.suggestion_history) == 0


def test_no_valid_recipes_returns_none():
    db = MagicMock()
    pasta = make_recipe("Pasta", ["italienisch"], recipe_id=1)
    db.query().all.return_value = [pasta]
    user = make_user(required_tags=["halal"])

    result = find_best_recipe(user, db)
    assert result is None


def test_no_recipe_in_db():
    db = MagicMock()
    db.query().all.return_value = []
    user = make_user(preference_tags=["asiatisch"])

    result = find_best_recipe(user, db)
    assert result is None


# empty_old_history Tests
def test_old_entries_removed():
    db = MagicMock()
    recipe = make_recipe("Curry", ["asiatisch"], recipe_id=1)
    old_entry = make_history_entry(recipe, hours_ago=HISTORY_DAYS * 24 + 1)
    user = make_user(history_entries=[old_entry])

    empty_old_history(user, db)
    db.delete.assert_called_once_with(old_entry)
    db.commit.assert_called()


def test_new_entries_added():
    db = MagicMock()
    recipe = make_recipe("Curry", ["asiatisch"], recipe_id=1)
    new_entry = make_history_entry(recipe, hours_ago=1)
    user = make_user(history_entries=[new_entry])

    empty_old_history(user, db)
    db.delete.assert_not_called()


# get_suggestion Tests
def test_user_not_found():
    db = MagicMock()
    db.query().filter().first.return_value = None
    assert get_suggestion(user_id=999, db=db) is None


def test_in_time_same_recipe():
    db = MagicMock()
    curry = make_recipe("Curry", ["asiatisch"], recipe_id=1)
    entry = make_history_entry(curry, hours_ago=1)  # vor 1 Stunde → noch im Cooldown
    user = make_user(preference_tags=["asiatisch"], history_entries=[entry])
    db.query().filter().first.return_value = user

    result = get_suggestion(user_id=1, db=db, skip=False)
    assert result == curry


def test_after_cooldown_new_recipe():
    curry = make_recipe("Curry", ["asiatisch"], recipe_id=1)
    pasta = make_recipe("Pasta", ["asiatisch"], recipe_id=2)
    entry = make_history_entry(curry, hours_ago=COOLDOWN_HOURS + 1)
    user = make_user(preference_tags=["asiatisch"], history_entries=[entry])

    db = MagicMock()
    # User-Query
    db.query(User).filter().first.return_value = user
    # Recipe-Query
    db.query(Recipe).all.return_value = [curry, pasta]

    result = get_suggestion(user_id=1, db=db, skip=False)
    assert result.title == "Pasta"


def test_skip_returns_different_recipe():
    db = MagicMock()
    curry = make_recipe("Curry", ["asiatisch"], recipe_id=1)
    pasta = make_recipe("Pasta", ["asiatisch"], recipe_id=2)
    entry = make_history_entry(curry, hours_ago=1)  # im Cooldown, aber skip=True
    user = make_user(preference_tags=["asiatisch"], history_entries=[entry])
    db.query().filter().first.return_value = user
    db.query().all.return_value = [curry, pasta]

    result = get_suggestion(user_id=1, db=db, skip=True)
    assert result.title == "Pasta"


def test_skip_no_alternative_returns_none():
    db = MagicMock()
    curry = make_recipe("Curry", ["asiatisch"], recipe_id=1)
    entry = make_history_entry(curry, hours_ago=1)
    user = make_user(preference_tags=["asiatisch"], history_entries=[entry])
    db.query().filter().first.return_value = user
    db.query().all.return_value = [curry]  # nur ein Rezept

    result = get_suggestion(user_id=1, db=db, skip=True)
    assert result is None


def test_first_call_no_history():
    db = MagicMock()
    curry = make_recipe("Curry", ["asiatisch"], recipe_id=1)
    user = make_user(preference_tags=["asiatisch"])
    db.query().filter().first.return_value = user
    db.query().all.return_value = [curry]

    result = get_suggestion(user_id=1, db=db)
    assert result.title == "Curry"


def test_suggestion_saved_in_history():
    db = MagicMock()
    curry = make_recipe("Curry", ["asiatisch"], recipe_id=1)
    user = make_user(preference_tags=["asiatisch"])
    db.query().filter().first.return_value = user
    db.query().all.return_value = [curry]

    get_suggestion(user_id=1, db=db)
    db.add.assert_called_once()
    db.commit.assert_called()

