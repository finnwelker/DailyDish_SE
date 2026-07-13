import hashlib
import time
from pathlib import Path
from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import inspect, text, func, distinct
from sqlalchemy.orm import Session, selectinload
from database import engine, Base, get_db, SessionLocal
from models import recipe, tag, join_tables
from models.user import User
from models.recipe import Recipe
from routers import recipeRout, userRout, tagRout, suggestionRout, favouriteRout
from seed import seed_database

BASE_DIR = Path(__file__).resolve().parent
Base.metadata.create_all(bind=engine)
seed_database()

app = FastAPI(title="DailyDish API")

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

def auth_context(request: Request) -> dict[str, bool | int]:
    return {"is_logged_in": bool(request.cookies.get("user_id")), "cache_version": int(time.time())}

def user_context(request: Request) -> dict[str, object]:
    # If the route already fetched the user from the right session (e.g. test DB),
    # use that directly so the context processor does not overwrite it.
    if hasattr(request.state, "user"):
        return {"user": request.state.user}

    user_id = request.cookies.get("user_id")
    if not user_id:
        return {"user": None}

    try:
        user_id_value = int(user_id)
    except ValueError:
        return {"user": None}

    db = SessionLocal()
    try:
        user = db.query(User).options(selectinload(User.tags)).filter(User.id == user_id_value).first()
        return {"user": user}
    finally:
        db.close()

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates"),
    context_processors=[auth_context, user_context],
)
app.state.templates = templates

app.include_router(recipeRout.router)
app.include_router(userRout.router)
app.include_router(userRout.auth_router)
app.include_router(tagRout.router)
app.include_router(suggestionRout.router)
app.include_router(favouriteRout.router)


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash

@app.get("/")
def root(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    try:
        user_id_value = int(user_id)
    except ValueError:
        return RedirectResponse(url="/login", status_code=303)

    user_exists = db.query(User.id).filter(User.id == user_id_value).first()
    if user_exists:
        return RedirectResponse(url="/dashboard", status_code=303)

    return RedirectResponse(url="/login", status_code=303)

@app.get("/dashboard")
def dashboard(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    current_user = None
    if user_id:
        try:
            user_id_value = int(user_id)
        except ValueError:
            user_id_value = None

        if user_id_value is not None:
            current_user = db.query(User).options(selectinload(User.tags)).filter(User.id == user_id_value).first()
            if current_user and not current_user.tags:
                return RedirectResponse(url="/choose-tags", status_code=303)

    request.state.user = current_user

    popularity_expr = (
        func.count(distinct(join_tables.user_tags.c.user_id))
        + func.count(distinct(join_tables.recipe_tags.c.recipe_id))
    )

    popular_tag_rows = (
        db.query(
            tag.Tag.name.label("name"),
            popularity_expr.label("usage_count"),
        )
        .outerjoin(join_tables.user_tags, tag.Tag.id == join_tables.user_tags.c.tag_id)
        .outerjoin(join_tables.recipe_tags, tag.Tag.id == join_tables.recipe_tags.c.tag_id)
        .group_by(tag.Tag.id, tag.Tag.name)
        .order_by(popularity_expr.desc(), tag.Tag.name.asc())
        .limit(12)
        .all()
    )

    popular_tags = [row.name for row in popular_tag_rows if row.name]

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {"request": request, "popular_tags": popular_tags},
    )


@app.get("/favourites")
def favourites_page(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    try:
        user_id_value = int(user_id)
    except ValueError:
        return RedirectResponse(url="/login", status_code=303)

    user = (
        db.query(User)
        .options(
            selectinload(User.favourite_recipes).selectinload(Recipe.tags)
        )
        .filter(User.id == user_id_value)
        .first()
    )
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    request.state.user = user
    return templates.TemplateResponse(
        request,
        "favourites.html",
        {"request": request, "favourites": user.favourite_recipes},
    )
