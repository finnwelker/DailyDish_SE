from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import seed
from database import Base, get_db
from main import app
from models.recipe import Recipe
from models.tag import Tag
from models.user import User
from routers.userRout import hash_password

TEST_DATABASE_URL = "sqlite:///./test_dailydish.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        db.add_all([
            Tag(name="Vegetarisch", is_required=True),
            Tag(name="Asiatisch", is_required=False),
            Tag(name="Schnell", is_required=False),
        ])
        db.commit()
    finally:
        db.close()


def test_new_user_login_redirects_to_tag_selection_page():
    reset_database()
    app.dependency_overrides[get_db] = override_get_db

    db = TestingSessionLocal()
    try:
        user = User(name="new_user", password=hash_password("secret"))
        db.add(user)
        db.commit()
        db.refresh(user)
    finally:
        db.close()

    client = TestClient(app)
    response = client.post("/login", data={"username": "new_user", "password": "secret"}, follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/choose-tags"

    app.dependency_overrides.clear()


def test_user_with_existing_tags_still_goes_to_dashboard():
    reset_database()
    app.dependency_overrides[get_db] = override_get_db

    db = TestingSessionLocal()
    try:
        tag = db.query(Tag).filter(Tag.name == "Asiatisch").one()
        user = User(name="tagged_user", password=hash_password("secret"), tags=[tag])
        db.add(user)
        db.commit()
        db.refresh(user)
    finally:
        db.close()

    client = TestClient(app)
    response = client.post("/login", data={"username": "tagged_user", "password": "secret"}, follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/dashboard"

    app.dependency_overrides.clear()


def test_dashboard_load_daily_dish_button_has_server_rendered_user_id():
    reset_database()
    app.dependency_overrides[get_db] = override_get_db

    db = TestingSessionLocal()
    try:
        tag_one = db.query(Tag).filter(Tag.name == "Asiatisch").one()
        tag_two = db.query(Tag).filter(Tag.name == "Schnell").one()
        user = User(name="dashboard_user", password=hash_password("secret"), tags=[tag_one, tag_two])
        db.add(user)
        db.commit()
        db.refresh(user)
    finally:
        db.close()

    client = TestClient(app)
    login_response = client.post(
        "/login",
        data={"username": "dashboard_user", "password": "secret"},
        follow_redirects=False,
    )

    assert login_response.status_code == 303
    assert login_response.headers["location"] == "/dashboard"

    dashboard_response = client.get("/dashboard")
    assert dashboard_response.status_code == 200
    dashboard_html = dashboard_response.text
    assert 'id="load-daily-dish-button"' in dashboard_html
    assert 'data-user-id=' in dashboard_html

    app.dependency_overrides.clear()


def test_dashboard_shows_user_tags_and_choose_tags_page_preselects_them():
    reset_database()
    app.dependency_overrides[get_db] = override_get_db

    db = TestingSessionLocal()
    try:
        tag_one = db.query(Tag).filter(Tag.name == "Asiatisch").one()
        tag_two = db.query(Tag).filter(Tag.name == "Schnell").one()
        user = User(name="dashboard_user", password=hash_password("secret"), tags=[tag_one, tag_two])
        db.add(user)
        db.commit()
        db.refresh(user)
    finally:
        db.close()

    client = TestClient(app)
    login_response = client.post(
        "/login",
        data={"username": "dashboard_user", "password": "secret"},
        follow_redirects=False,
    )

    assert login_response.status_code == 303
    assert login_response.headers["location"] == "/dashboard"

    dashboard_response = client.get("/dashboard")
    assert dashboard_response.status_code == 200
    dashboard_html = dashboard_response.text
    assert "Meine Tags" in dashboard_html
    assert "Asiatisch" in dashboard_html
    assert "Schnell" in dashboard_html
    assert "Tags bearbeiten" in dashboard_html

    choose_tags_response = client.get("/choose-tags")
    assert choose_tags_response.status_code == 200
    choose_tags_html = choose_tags_response.text
    assert f'class="tag-pill tag-pill-button selected" data-tag-id="{tag_one.id}"' in choose_tags_html
    assert f'class="tag-pill tag-pill-button selected" data-tag-id="{tag_two.id}"' in choose_tags_html

    app.dependency_overrides.clear()


def test_seed_database_refreshes_existing_seeded_recipe_data(monkeypatch):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        for tag_name in ["Vegetarisch", "Vegan", "Halal", "Glutenfrei", "Laktosefrei", "Enthält keine Nüsse", "Asiatisch", "Leicht", "Schnell", "Thai", "Vietnamesisch", "Chinesisch"]:
            db.add(Tag(name=tag_name, is_required=tag_name in {"Vegetarisch", "Vegan", "Halal", "Glutenfrei", "Laktosefrei", "Enthält keine Nüsse"}))
        db.commit()

        recipe = Recipe(
            title="Gemüsecurry",
            description="alte Beschreibung",
            ingredients="alte Zutaten",
            instructions="alte Anleitung",
            tags=[
                db.query(Tag).filter(Tag.name == "Vegetarisch").one(),
                db.query(Tag).filter(Tag.name == "Vegan").one(),
                db.query(Tag).filter(Tag.name == "Halal").one(),
                db.query(Tag).filter(Tag.name == "Glutenfrei").one(),
                db.query(Tag).filter(Tag.name == "Laktosefrei").one(),
                db.query(Tag).filter(Tag.name == "Enthält keine Nüsse").one(),
                db.query(Tag).filter(Tag.name == "Asiatisch").one(),
                db.query(Tag).filter(Tag.name == "Leicht").one(),
                db.query(Tag).filter(Tag.name == "Schnell").one(),
                db.query(Tag).filter(Tag.name == "Thai").one(),
                db.query(Tag).filter(Tag.name == "Vietnamesisch").one(),
                db.query(Tag).filter(Tag.name == "Chinesisch").one(),
            ],
        )
        db.add(recipe)
        db.commit()
    finally:
        db.close()

    monkeypatch.setattr(seed, "SessionLocal", TestingSessionLocal)
    seed.seed_database()

    db = TestingSessionLocal()
    try:
        refreshed_description = db.query(Recipe.description).filter(Recipe.title == "Gemüsecurry").scalar()
        refreshed_ingredients = db.query(Recipe.ingredients).filter(Recipe.title == "Gemüsecurry").scalar()
        refreshed_instructions = db.query(Recipe.instructions).filter(Recipe.title == "Gemüsecurry").scalar()

        assert refreshed_description == "Ein veganes Gemüsecurry mit Kokosmilch und Reis"
        assert "250g Reis" in refreshed_ingredients
        assert "Reis nach Packungsanweisungen kochen" in refreshed_instructions
    finally:
        db.close()
