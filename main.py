from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from database import engine, Base
from models import user, recipe, tag, join_tables
from routers import recipeRout, userRout, tagRout, suggestionRout

BASE_DIR = Path(__file__).resolve().parent
Base.metadata.create_all(bind=engine)

app = FastAPI(title="DailyDish API")

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app.include_router(recipeRout.router)
app.include_router(suggestionRout.router)

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