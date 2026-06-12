from fastapi import FastAPI
from database import engine, Base
import models.recipe
from routers import recipeRout

Base.metadata.create_all(bind=engine)

app = FastAPI(title="DailyDish API")

app.include_router(recipeRout.router)

@app.get("/")
def root():
    return {"message": "DailyDish API läuft!"}