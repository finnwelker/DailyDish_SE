from database import SessionLocal, engine, Base
from models.recipe import Recipe
from models.tag import Tag
from models.user import User
import models.join_tables  # damit SQLAlchemy die Join-Tabellen kennt

Base.metadata.create_all(bind=engine)


def _build_tag_catalog():
    # Verbindende Tags anlegen
    vegetarisch = Tag(name="Vegetarisch", is_required=True)
    vegan = Tag(name="Vegan", is_required=True)
    halal = Tag(name="Halal", is_required=True)
    laktosefrei = Tag(name="Laktosefrei", is_required=True)
    glutenfrei = Tag(name="Glutenfrei", is_required=True)
    nonuts = Tag(name="Enthält keine Nüsse", is_required=True)

    # "Flavour-Tags" anlegen
    italienisch = Tag(name="Italienisch", is_required=False)
    asiatisch = Tag(name="Asiatisch", is_required=False)
    mediterran = Tag(name="Mediterran", is_required=False)
    tuerkisch = Tag(name="Türkisch", is_required=False)
    mexikanisch = Tag(name="Mexikanisch", is_required=False)
    chinesisch = Tag(name="Chinesisch", is_required=False)
    japanisch = Tag(name="Japanisch", is_required=False)
    thai = Tag(name="Thai", is_required=False)
    vietnamesisch = Tag(name="Vietnamesisch", is_required=False)
    karibisch = Tag(name="Karibisch", is_required=False)
    afrikanisch = Tag(name="Afrikanisch", is_required=False)
    amerikanisch = Tag(name="Amerikanisch", is_required=False)
    deutsch = Tag(name="Deutsch", is_required=False)
    franzoesisch = Tag(name="Französisch", is_required=False)

    # Adjektiv-Tags anlegen
    scharf = Tag(name="Scharf", is_required=False)
    suess = Tag(name="Süß", is_required=False)
    salzig = Tag(name="Salzig", is_required=False)
    deftig = Tag(name="Deftig", is_required=False)
    leicht = Tag(name="Leicht", is_required=False)
    einfach = Tag(name="Einfach", is_required=False)
    schnell = Tag(name="Schnell", is_required=False)
    dauert = Tag(name="Dauert", is_required=False)
    komplex = Tag(name="Komplex", is_required=False)

    return {
        "Vegetarisch": vegetarisch,
        "Vegan": vegan,
        "Halal": halal,
        "Laktosefrei": laktosefrei,
        "Glutenfrei": glutenfrei,
        "Enthält keine Nüsse": nonuts,
        "Italienisch": italienisch,
        "Asiatisch": asiatisch,
        "Mediterran": mediterran,
        "Türkisch": tuerkisch,
        "Mexikanisch": mexikanisch,
        "Chinesisch": chinesisch,
        "Japanisch": japanisch,
        "Thai": thai,
        "Vietnamesisch": vietnamesisch,
        "Karibisch": karibisch,
        "Afrikanisch": afrikanisch,
        "Amerikanisch": amerikanisch,
        "Deutsch": deutsch,
        "Französisch": franzoesisch,
        "Scharf": scharf,
        "Süß": suess,
        "Salzig": salzig,
        "Deftig": deftig,
        "Leicht": leicht,
        "Einfach": einfach,
        "Schnell": schnell,
        "Dauert": dauert,
        "Komplex": komplex,
    }


def _build_seed_recipes(tag_lookup: dict[str, Tag]):
    return [
        {
            "title": "Gemüsecurry",
            "description": "Ein veganes Gemüsecurry mit Kokosmilch und Reis",
            "ingredients": "250g Reis, 500ml Kokosmilch, Paprika, Zwiebeln, Sojasprossen, Salz, Weißer Pfeffer, Kreuzkümmel, Chilipulver",
            "instructions": "1. Reis nach Packungsanweisungen kochen. 2. Zwiebeln und anderes Gemüse anbraten. 3. Würzen 4. Kokosmilch hinzugeben 5. ggf. Nachwürzen und mit Reis servieren",
            "tag_names": [
                "Vegetarisch", "Vegan", "Halal", "Glutenfrei", "Laktosefrei", "Enthält keine Nüsse",
                "Asiatisch", "Leicht", "Schnell", "Thai", "Vietnamesisch", "Chinesisch"
            ],
        },
        {
            "title": "Spaghetti Bolognese",
            "description": "Ein klassisches italienisches Gericht",
            "ingredients": "Spaghetti, 500 Hack, 500ml passierte Tomaten, Tomatenmark, Zwiebeln, Karotten, ggf. Staudensellerie, Salz, Pfeffer, Chilipulver, Basilikum, Knoblauch",
            "instructions": "1. Zwiebeln und anderes Gemüse anbraten. 2. Wenn gewollt, Knoblauch hinzufügen (aufpassen, dass dieser nicht anbrennt) 3. Hack hinzugeben und anbraten, Tomatenmark ebenfalls 4. Würzen und passierte Tomaten hinzugeben 5. mind. halbe Stunde köcheln lassen 6. Nudeln nach Packungsanweisungen kochen und zur Bolognese hinzugeben 7. ggf. Nachwürzen und mit frischem Basilikum servieren",
            "tag_names": ["Laktosefrei", "Halal", "Enthält keine Nüsse", "Italienisch", "Deftig", "Dauert", "Einfach"],
        },
        {
            "title": "Jerk Chicken",
            "description": "Ein Klassiker aus Jamaika",
            "ingredients": "500g Huhn (Brust oder Keule), Frühlingszwiebeln, Ingwer, Knoblauch, Chilis, brauner Zucker, Piment, Zimt, Muskatnuss, Limettensaft, Öl",
            "instructions": "1. Alle Zutaten bis auf das Fleisch zusammenfügen und pürieren. 2. Über Nacht das Fleisch marinieren lassen 3. Auf dem Grill oder im Ofen bei 180° garen bis das Fleisch knusprig ist.",
            "tag_names": ["Laktosefrei", "Halal", "Enthält keine Nüsse", "Karibisch", "Deftig", "Einfach", "Dauert"],
        },
        {
            "title": "Zucchini-Frikadellen",
            "description": "Leckere vegetarische Zucchini-Puffer",
            "ingredients": "2-3 Zucchinis, 1-2 Eier, Zwiebeln, Knoblauch, Mehl/Paniermehl oder Reis, Öl, Salz, Pfeffer, Paprikapulver, Muskatnuss",
            "instructions": "1. Die Zwiebeln, Knoblauch und Zucchinis reiben. 2. Gemüse und Gewürze mit Eiern vermengen. 3. Zusammen mit etwas Mehl oder ein wenig gekochtem Reis zu kleinen Fladen formen. 4. In etwas Öl scharf anbraten.",
            "tag_names": ["Vegetarisch", "Halal", "Laktosefrei", "Enthält keine Nüsse", "Leicht", "Einfach", "Schnell"],
        },
        {
            "title": "Shakshuka",
            "description": "Nordafrikanisches Gericht mit Eiern in würziger Tomatensauce",
            "ingredients": "4 Eier, 400g gehackte Tomaten, 1 Paprika, 1 Zwiebel, Knoblauch, Kreuzkümmel, Paprikapulver, Chili, Feta optional",
            "instructions": "1. Zwiebeln und Paprika anbraten. 2. Gewürze und Tomaten hinzufügen. 3. Eier direkt in die Sauce aufschlagen. 4. Eier abgedeckt pochieren.",
            "tag_names": ["Vegetarisch", "Laktosefrei", "Afrikanisch", "Scharf", "Mediterran", "Enthält keine Nüsse", "Halal"],
        },
        {
            "title": "Pad Thai",
            "description": "Klassischer thailändischer gebratener Reisnudeln mit Erdnüssen",
            "ingredients": "200g Reisnudeln, 2 Eier, 100g Tofu, Sojasprossen, Frühlingszwiebeln, Erdnüsse, Tamarindenpaste, Fischsauce, Zucker, Limette",
            "instructions": "1. Nudeln einweichen. 2. Tofu anbraten. 3. Eier gerührt dazugeben. 4. Nudeln und Sauce hinzufügen. 5. Mit Sprossen, Erdnüssen und Limette servieren.",
            "tag_names": ["Vegetarisch", "Thai", "Scharf", "Asiatisch", "Halal"],
        },
        {
            "title": "Hummus Bowl",
            "description": "Mediterrane Bowl mit selbstgemachtem Hummus und geröstetem Gemüse",
            "ingredients": "400g Kichererbsen, Tahini, Zitrone, Knoblauch, Olivenöl, Paprika, Zucchini, Kirschtomaten, Fladenbrot",
            "instructions": "1. Kichererbsen mit Tahini, Zitrone und Knoblauch pürieren. 2. Gemüse mit Olivenöl rösten. 3. Alles auf dem Hummus anrichten.",
            "tag_names": ["Vegan", "Vegetarisch", "Laktosefrei", "Mediterran", "Leicht", "Einfach", "Halal"],
        },
        {
            "title": "Pizza Margherita",
            "description": "Klassische neapolitanische Pizza mit Tomatensauce und Mozzarella",
            "ingredients": "300g Mehl, Hefe, Salz, Olivenöl, 200g Tomaten passiert, 150g Mozzarella, frisches Basilikum",
            "instructions": "1. Teig kneten und mind 1h gehen lassen, opt. über Nacht. 2. Dünn ausrollen. 3. Mit gewürzter Tomatensauce und Mozzarella belegen. 4. Bei 250°C 10 Min backen.",
            "tag_names": ["Vegetarisch", "Mediterran", "Italienisch", "Halal"],
        },
        {
            "title": "Zwiebelrostbraten",
            "description": "Klassisches deutsches Schmorgericht mit Röstzwiebeln und Bratensoße",
            "ingredients": "600g Rostbraten, 4 Zwiebeln, Butterschmalz, Rinderbrühe, Rotwein, Thymian, Lorbeer, Salz, Pfeffer, Spätzle",
            "instructions": "1. Fleisch scharf anbraten. 2. Zwiebeln karamellisieren. 3. Mit Rotwein ablöschen. 4. Brühe und Kräuter dazu. 5. 1h schmoren. 6. Mit Spätzle servieren.",
            "tag_names": ["Deutsch", "Deftig", "Komplex", "Halal", "Dauert"],
        },
        {
            "title": "Avocado Toast",
            "description": "Schnelles Frühstück mit Avocado, Ei und Chiliflocken",
            "ingredients": "2 Scheiben Vollkornbrot, 1 Avocado, 2 Eier, Chiliflocken, Limettensaft, Salz, Pfeffer, optional Fetakäse",
            "instructions": "1. Brot toasten. 2. Avocado mit Limettensaft und Salz zerdrücken. 3. Eier nach Wahl zubereiten. 4. Alles auf das Brot legen und mit Chiliflocken bestreuen.",
            "tag_names": ["Vegetarisch", "Schnell", "Leicht", "Halal", "Laktosefrei"],
        },
    ]


def seed_database():
    db = SessionLocal()
    try:
        existing_tag_names = {tag.name.lower() for tag in db.query(Tag).all()}
        tag_catalog = _build_tag_catalog()
        tags_to_add = [tag for name, tag in tag_catalog.items() if name.lower() not in existing_tag_names]

        if tags_to_add:
            db.add_all(tags_to_add)
            db.commit()

        tag_lookup: dict[str, Tag] = {}
        for tag in db.query(Tag).all():
            tag_lookup[str(tag.name)] = tag

        for recipe_data in _build_seed_recipes(tag_lookup):
            recipe = db.query(Recipe).filter(Recipe.title == recipe_data["title"]).first()
            if recipe is None:
                recipe = Recipe(
                    title=recipe_data["title"],
                    description=recipe_data["description"],
                    ingredients=recipe_data["ingredients"],
                    instructions=recipe_data["instructions"],
                )
                db.add(recipe)
                db.flush()

            recipe.description = recipe_data["description"]
            recipe.ingredients = recipe_data["ingredients"]
            recipe.instructions = recipe_data["instructions"]
            recipe.tags = [tag_lookup[name] for name in recipe_data["tag_names"]]

        db.commit()

        if db.query(User).count() == 0:
            user1 = User(name="Jesse", password="test", tags=[db.query(Tag).filter(Tag.name == "Italienisch").first(), db.query(Tag).filter(Tag.name == "Asiatisch").first()])
            user2 = User(name="Finn", password="test", tags=[db.query(Tag).filter(Tag.name == "Vegetarisch").first(), db.query(Tag).filter(Tag.name == "Italienisch").first(), db.query(Tag).filter(Tag.name == "Asiatisch").first()])
            user3 = User(name="Anna", password="test", tags=[db.query(Tag).filter(Tag.name == "Vegan").first(), db.query(Tag).filter(Tag.name == "Asiatisch").first()])
            db.add_all([user1, user2, user3])
            db.commit()
    finally:
        db.close()


seed_database()
print("Seeding database")
