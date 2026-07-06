from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from schemas.userSchema import UserCreate, UserResponse
import hashlib

router = APIRouter(prefix="/user", tags=["user"])
auth_router = APIRouter(tags=["auth"])


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash


@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/", response_model=list[UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@auth_router.get("/signup")
def signup_form(request: Request):
    return request.app.state.templates.TemplateResponse(
        request,
        "signup.html",
        {"request": request}
    )


@auth_router.post("/signup")
async def signup_submit(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    username = str(form.get("username", "")).strip()
    password = str(form.get("password", ""))

    if not username or not password:
        return request.app.state.templates.TemplateResponse(
            request,
            "signup.html",
            {"request": request, "error": "Bitte gib einen Benutzernamen und ein Passwort ein."}
        )

    existing_user = db.query(User).filter(User.name == username).first()
    if existing_user:
        return request.app.state.templates.TemplateResponse(
            request,
            "signup.html",
            {"request": request, "error": "Dieser Benutzername existiert bereits."}
        )

    new_user = User(name=username, password=hash_password(password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return RedirectResponse(url="/login", status_code=303)


@auth_router.get("/login")
def login_form(request: Request):
    return request.app.state.templates.TemplateResponse(
        request,
        "login.html",
        {"request": request}
    )


@auth_router.post("/login")
async def login_submit(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    username = str(form.get("username", "")).strip()
    password = str(form.get("password", ""))

    if not username or not password:
        return request.app.state.templates.TemplateResponse(
            request,
            "login.html",
            {"request": request, "error": "Bitte gib deinen Benutzernamen und dein Passwort ein."}
        )

    user = db.query(User).filter(User.name == username).first()
    if not user or not verify_password(password, str(user.password)):
        return request.app.state.templates.TemplateResponse(
            request,
            "login.html",
            {"request": request, "error": "Benutzername oder Passwort ist ungültig."}
        )

    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie("user_id", str(user.id), httponly=True, samesite="lax")
    return response


@auth_router.get("/logout")
def logout(request: Request):
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("user_id")
    return response
