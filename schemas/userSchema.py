from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    password: str


class UserResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True  # Um SQLAlchemy Sachen zu konvertieren
