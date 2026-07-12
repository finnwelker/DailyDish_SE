from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
from models.tag import Tag
from models.user import User
from schemas.userSchema import UserCreate, UserResponse
import hashlib

router = APIRouter(prefix="/user", tags=["user"])
auth_router = APIRouter(tags=["auth"])


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash


def get_authenticated_user(request: Request, db: Session):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return None

    try:
        user_id_value = int(user_id)
    except ValueError:
        return None

    return db.query(User).filter(User.id == user_id_value).first()


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

    next_page = "/dashboard" if user.tags else "/choose-tags"
    response = RedirectResponse(url=next_page, status_code=303)
    response.set_cookie("user_id", str(user.id), httponly=True, samesite="lax")
    return response


@auth_router.get("/choose-tags")
def choose_tags_form(request: Request, db: Session = Depends(get_db)):
    user = get_authenticated_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    tags = db.query(Tag).order_by(Tag.name).all()
    selected_tag_ids = [tag.id for tag in user.tags]
    return request.app.state.templates.TemplateResponse(
        request,
        "choose_tags.html",
        {
            "request": request,
            "user": user,
            "tags": tags,
            "selected_tag_ids": selected_tag_ids,
        }
    )


@auth_router.post("/choose-tags")
async def save_selected_tags(request: Request, db: Session = Depends(get_db)):
    user = get_authenticated_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    form = await request.form()
    selected_tag_ids = [int(tag_id) for tag_id in form.getlist("tag_ids") if str(tag_id).strip()]
    selected_tags = db.query(Tag).filter(Tag.id.in_(selected_tag_ids)).all()

    user.tags = selected_tags
    db.commit()

    return RedirectResponse(url="/dashboard", status_code=303)


@auth_router.get("/logout")
def logout(request: Request):
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("user_id")
    return response
