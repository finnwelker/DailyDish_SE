from fastapi import FastAPI
from database import engine, Base
from models import user, recipe, tag, join_tables
from routers import recipeRout, userRout, tagRout, suggestionRout

Base.metadata.create_all(bind=engine)

app = FastAPI(title="DailyDish API")

app.include_router(recipeRout.router)
app.include_router(suggestionRout.router)

@app.get("/")
def root():
    return {"message": "DailyDish API läuft!"}