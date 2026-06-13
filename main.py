from fastapi import FastAPI
from database import engine, Base
from models import user, recipe, tag, join_tables
from routers import recipeRout, userRout, tagRout

Base.metadata.create_all(bind=engine)

app = FastAPI(title="DailyDish API")

app.include_router(recipeRout.router)

@app.get("/")
def root():
    return {"message": "DailyDish API läuft!"}