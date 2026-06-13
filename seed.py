from database import SessionLocal, engine, Base
from models.recipe import Recipe
from models.tag import Tag
from models.user import User
import models.join_tables  # damit SQLAlchemy die Join-Tabellen kennt

Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Tags anlegen
vegetarisch = Tag(name="Vegetarisch")
vegan = Tag(name="Vegan")
laktosefrei = Tag(name="Laktosefrei")
italienisch = Tag(name="Italienisch")
asiatisch = Tag(name="Asiatisch")

db.add_all([vegetarisch, vegan, laktosefrei, italienisch, asiatisch])

# Rezepte anlegen

rezept1 = Recipe(
    title="Gemüsecurry",
    description="Ein veganes Gemüsecurry mit Kokosmilch und Reis",
    ingredients="250g Reis, 500ml Kokosmilch, div. Gemüse (Paprika, Zwiebeln, Sojasprossen, etc.), Gewürze (Salz, weißer Pfeffer, Kreuzkümmel, Chilipulver)",
    instructions="1. Reis nach Packungsanweisungen kochen. 2. Zwiebeln und anderes Gemüse anbraten. 3. Würzen 4. Kokosmilch hinzugeben 5. ggf. Nachwürzen und mit Reis servieren",
    tags = [vegetarisch, vegan, laktosefrei, asiatisch]
)
rezept2 = Recipe(
    title="Spaghetti Bolognese",
    description="Ein klassisches italienisches Gericht",
    ingredients="500 Hack, 500ml passierte Tomaten, Tomatenmark, Zwiebeln, Karotten und ggf. Staudensellerie, Gewürze (Salz, Pfeffer, *Chilipulver, Basilikum), *Knoblauch, Tagliatelle",
    instructions="1. Zwiebeln und anderes Gemüse anbraten. 2. Wenn gewollt, Knoblauch hinzufügen (aufpassen, dass dieser nicht anbrennt) 3. Hack hinzugeben und anbraten, Tomatenmark ebenfalls"
                 "3. Würzen und passierte Tomaten hinzugeben 4. mind. halbe Stunde köcheln lassen 5. Nudeln nach Packungsanweisungen kochen und zur Bolognese hinzugeben 6. ggf. Nachwürzen und mit frischem Basilikum servieren",
    tags = [laktosefrei, italienisch]
)

db.add_all([rezept1, rezept2])
db.commit()

# User anlegen
user1 = User(name="Jesse", tags=[italienisch, asiatisch])
user2 = User(name="Finn", tags=[vegetarisch, italienisch, asiatisch])
user3 = User(name="Anna", tags=[vegan, asiatisch])

db.add_all([user1, user2, user3])
db.commit()

db.close()
print("Seeding database")
