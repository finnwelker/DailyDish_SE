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


def seed_database():
    db = SessionLocal()
    try:
        existing_tag_names = {tag.name.lower() for tag in db.query(Tag).all()}
        tag_catalog = _build_tag_catalog()
        tags_to_add = [tag for name, tag in tag_catalog.items() if name.lower() not in existing_tag_names]

        if tags_to_add:
            db.add_all(tags_to_add)
            db.commit()

        db.commit()

        if db.query(Recipe).count() == 0:
            tag_lookup: dict[str, Tag] = {}
            for tag in db.query(Tag).all():
                tag_lookup[str(tag.name)] = tag

            rezept1 = Recipe(
                title="Gemüsecurry",
                description="Ein veganes Gemüsecurry mit Kokosmilch und Reis",
                ingredients="250g Reis, 500ml Kokosmilch, div. Gemüse (Paprika, Zwiebeln, Sojasprossen, etc.), Gewürze (Salz, weißer Pfeffer, Kreuzkümmel, Chilipulver)",
                instructions="1. Reis nach Packungsanweisungen kochen. 2. Zwiebeln und anderes Gemüse anbraten. 3. Würzen 4. Kokosmilch hinzugeben 5. ggf. Nachwürzen und mit Reis servieren",
                tags=[
                    tag_lookup["Vegetarisch"], tag_lookup["Vegan"], tag_lookup["Halal"], tag_lookup["Glutenfrei"], tag_lookup["Laktosefrei"], tag_lookup["Enthält keine Nüsse"],
                    tag_lookup["Asiatisch"], tag_lookup["Leicht"], tag_lookup["Schnell"], tag_lookup["Thai"], tag_lookup["Vietnamesisch"], tag_lookup["Chinesisch"]
                ]
            )
            rezept2 = Recipe(
                title="Spaghetti Bolognese",
                description="Ein klassisches italienisches Gericht",
                ingredients="500 Hack, 500ml passierte Tomaten, Tomatenmark, Zwiebeln, Karotten und ggf. Staudensellerie, Gewürze (Salz, Pfeffer, *Chilipulver, Basilikum), *Knoblauch, Tagliatelle",
                instructions="1. Zwiebeln und anderes Gemüse anbraten. 2. Wenn gewollt, Knoblauch hinzufügen (aufpassen, dass dieser nicht anbrennt) 3. Hack hinzugeben und anbraten, Tomatenmark ebenfalls"
                             "3. Würzen und passierte Tomaten hinzugeben 4. mind. halbe Stunde köcheln lassen 5. Nudeln nach Packungsanweisungen kochen und zur Bolognese hinzugeben 6. ggf. Nachwürzen und mit frischem Basilikum servieren",
                tags=[tag_lookup["Laktosefrei"], tag_lookup["Halal"], tag_lookup["Enthält keine Nüsse"], tag_lookup["Italienisch"], tag_lookup["Deftig"], tag_lookup["Dauert"], tag_lookup["Einfach"]]
            )
            rezept3 = Recipe(
                title="Jerk Chicken",
                description="Ein Klassiker aus Jamaika",
                ingredients="500g Huhn (Brust oder Keule), Frühlingszwiebeln, Ingwer, Knoblauch, Chilis, brauner Zucker, Piment, Zimt, Muskatnuss, Limettensaft, Öl",
                instructions="1. Alle Zutaten bis auf das Fleisch zusammenfügen und pürieren. 2. Über Nacht das Fleisch marinieren lassen 3. Auf dem Grill oder im Ofen bei 180° garen bis das Fleiscch knusprig ist.",
                tags=[tag_lookup["Laktosefrei"], tag_lookup["Halal"], tag_lookup["Enthält keine Nüsse"], tag_lookup["Karibisch"], tag_lookup["Deftig"], tag_lookup["Einfach"], tag_lookup["Dauert"]]
            )

            rezept4 = Recipe(
                title="Zucchini-Frikadellen",
                description="Leckere vegetarische Zucchini-Puffer",
                ingredients="2-3 Zucchinis, 1-2 Eier, Zwiebeln, Knoblauch, Mehl/Paniermehl oder Reis, Öl, Salz, Pfeffer, Paprikapulver, Muskatnuss",
                instructions="1. Die Zwiebeln, Knoblauch und Zucchinis reiben. 2. Gemüse und Gewürze mit Eiern vermengen. 3. Zusammen mit etwas Mehl oder ein wenig gekochtem Reis zu kleinen Fladen formen. 4. In etwas Öl scharf anbraten.",
                tags=[tag_lookup["Vegetarisch"], tag_lookup["Halal"], tag_lookup["Laktosefrei"], tag_lookup["Enthält keine Nüsse"], tag_lookup["Leicht"], tag_lookup["Einfach"], tag_lookup["Schnell"]]
            )

            db.add_all([rezept1, rezept2, rezept3, rezept4])
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
