from pathlib import Path
import hashlib
from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session
from database import engine, Base, get_db, SessionLocal
from models import recipe, tag, join_tables
from models.user import User
from routers import recipeRout, userRout, tagRout, suggestionRout

BASE_DIR = Path(__file__).resolve().parent
Base.metadata.create_all(bind=engine)

# Ensure the users table has a password column if the database already existed
inspector = inspect(engine)
if "users" in inspector.get_table_names():
    columns = [column.get("name") for column in inspector.get_columns("users")]
    if "password" not in columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN password VARCHAR"))

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

app.include_router(recipeRout.router)
app.include_router(userRout.router)
app.include_router(tagRout.router)
app.include_router(suggestionRout.router)


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


@app.get("/signup")
def signup_form(request: Request):
    return templates.TemplateResponse(
        request,
        "signup.html",
        {"request": request}
    )


@app.post("/signup")
async def signup_submit(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    username = form.get("username", "").strip()
    password = form.get("password", "")

    if not username or not password:
        return templates.TemplateResponse(
            request,
            "signup.html",
            {"request": request, "error": "Bitte gib einen Benutzernamen und ein Passwort ein."}
        )

    existing_user = db.query(User).filter(User.name == username).first()
    if existing_user:
        return templates.TemplateResponse(
            request,
            "signup.html",
            {"request": request, "error": "Dieser Benutzername existiert bereits."}
        )

    new_user = User(name=username, password=hash_password(password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return RedirectResponse(url="/login", status_code=303)


@app.get("/login")
def login_form(request: Request):
    return templates.TemplateResponse(
        request,
        "login.html",
        {"request": request}
    )


@app.post("/login")
async def login_submit(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    username = form.get("username", "").strip()
    password = form.get("password", "")

    if not username or not password:
        return templates.TemplateResponse(
            request,
            "login.html",
            {"request": request, "error": "Bitte gib deinen Benutzernamen und dein Passwort ein."}
        )

    user = db.query(User).filter(User.name == username).first()
    if not user or not verify_password(password, user.password):
        return templates.TemplateResponse(
            request,
            "login.html",
            {"request": request, "error": "Benutzername oder Passwort ist ungültig."}
        )

    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie("user_id", str(user.id), httponly=True, samesite="lax")
    return response


@app.get("/logout")
def logout(request: Request):
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("user_id")
    return response
