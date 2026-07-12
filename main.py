import hashlib
from pathlib import Path
from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session, selectinload
from database import engine, Base, get_db, SessionLocal
from models import recipe, tag, join_tables
from models.user import User
from routers import recipeRout, userRout, tagRout, suggestionRout, favouriteRout
from seed import seed_database

BASE_DIR = Path(__file__).resolve().parent
Base.metadata.create_all(bind=engine)
seed_database()

app = FastAPI(title="DailyDish API")

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

def auth_context(request: Request) -> dict[str, bool]:
    return {"is_logged_in": bool(request.cookies.get("user_id"))}

def user_context(request: Request) -> dict[str, object]:
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
def root():
    return {"message": "DailyDish API läuft!"}

@app.get("/dashboard")
def dashboard(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if user_id:
        try:
            user_id_value = int(user_id)
        except ValueError:
            user_id_value = None

        if user_id_value is not None:
            user = db.query(User).filter(User.id == user_id_value).first()
            if user and not user.tags:
                return RedirectResponse(url="/choose-tags", status_code=303)

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {"request": request}
    )


