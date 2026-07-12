from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, get_db
from main import app
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
        tag = db.query(Tag).filter(Tag.name == "Asiatisch").first()
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


def test_dashboard_shows_user_tags_and_choose_tags_page_preselects_them():
    reset_database()
    app.dependency_overrides[get_db] = override_get_db

    db = TestingSessionLocal()
    try:
        tag_one = db.query(Tag).filter(Tag.name == "Asiatisch").first()
        tag_two = db.query(Tag).filter(Tag.name == "Schnell").first()
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
    assert "Tag-Auswahl bearbeiten" in dashboard_html

    choose_tags_response = client.get("/choose-tags")
    assert choose_tags_response.status_code == 200
    choose_tags_html = choose_tags_response.text
    assert f'class="tag-pill tag-pill-button selected" data-tag-id="{tag_one.id}"' in choose_tags_html
    assert f'class="tag-pill tag-pill-button selected" data-tag-id="{tag_two.id}"' in choose_tags_html

    app.dependency_overrides.clear()
