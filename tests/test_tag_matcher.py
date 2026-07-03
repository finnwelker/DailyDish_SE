from services.tag_matcher import calculate_score, get_suggestion
from unittest.mock import MagicMock


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


# get_suggestion Tests-Setup

def make_tag(name, is_required = False):
    tag = MagicMock()
    tag.name = name
    tag.is_required = is_required
    return tag


def make_recipe(title, tag_names):
    recipe = MagicMock()
    recipe.title = title
    recipe.tags = [make_tag(n) for n in tag_names]
    return recipe


def make_user(tag_names, required=None):
    user = MagicMock()
    all_tags = []
    for name in tag_names:
        is_req = required and name in required
        all_tags.append(make_tag(name, is_required=is_req))
    user.tags = all_tags
    return user


# get_suggestion Tests
def test_best_recipe():
    db = MagicMock()
    user = make_user(["asiatisch", "vegan"])
    curry = make_recipe("Curry", ["asiatisch", "vegan", "vegetarisch"])
    pasta = make_recipe("Pasta", ["italienisch"])
    db.query().filter().first.return_value = user
    db.query().all.return_value = [curry, pasta]

    result = get_suggestion(user_id =1, db=db)
    assert result.title == "Curry"


def user_not_found():
    db = MagicMock()
    db.query().filter().first.return_value = None
    assert get_suggestion(user_id =999, db=db) is None


def test_mandatory_tag_filters_recipe():
    db = MagicMock()
    user = make_user(["vegetarisch", "asiatisch"], required=["vegetarisch"])
    fleisch = make_recipe("Fleischgericht", ["asiatisch"])       # kein vegetarisch --> rausgefiltert
    curry = make_recipe("Curry", ["vegetarisch", "asiatisch"]) # hat vegetarisch --> bleibt
    db.query().filter().first.return_value = user
    db.query().all.return_value = [fleisch, curry]

    result = get_suggestion(user_id =1, db=db)
    assert result.title == "Curry"


def test_no_valid_recipes():
    db = MagicMock()
    user = make_user(["vegetarisch", "asiatisch"], required=["vegetarisch"])
    fleisch = make_recipe("Fleischgericht", ["asiatisch"])       # kein vegetarisch --> rausgefiltert
    curry = make_recipe("Curry", ["asiatisch"]) # ebenfalls kein vegetarisch --> keine validen Rezepte
    db.query().filter().first.return_value = user
    db.query().all.return_value = [fleisch, curry]

    result = get_suggestion(user_id =1, db=db)
    assert result is None


def test_user_without_tags():
    db = MagicMock()
    user = make_user([])
    curry = make_recipe("Curry", ["vegetarisch", "asiatisch"])
    db.query().filter().first.return_value = user
    db.query().all.return_value = [curry]

    result = get_suggestion(user_id =1, db=db)

    assert result is not None