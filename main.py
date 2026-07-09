import hashlib
from pathlib import Path
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session
from database import engine, Base, get_db, SessionLocal
from models import recipe, tag, join_tables
from models.user import User
from routers import recipeRout, userRout, tagRout, suggestionRout, favouriteRouter

BASE_DIR = Path(__file__).resolve().parent
Base.metadata.create_all(bind=engine)

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
        user = db.query(User).filter(User.id == user_id_value).first()
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
app.include_router(favouriteRouter.router)


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash

@app.get("/")
def root():
    return {"message": "DailyDish API läuft!"}

@app.get("/dashboard")
def dashboard(request: Request):
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {"request": request}
    )


