from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str


class UserResponse(BaseModel):
    name: str

    class Config:
        from_attributes = True  # Um SQLAlchemy Sachen zu konvertieren
