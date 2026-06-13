# Tag Schema und Router um später alle Tags zur Auswahl anzeigen zu lassen, sonst könnten wir die nur mit Anlegen der User/Rezepte benutzen
from pydantic import BaseModel


class Tag(BaseModel):
    name: str


class TagResponse(BaseModel):
    id: int
    name: str

    class Config(BaseModel):
        from_attributes = True  # Um SQLAlchemy Sachen zu konvertieren
