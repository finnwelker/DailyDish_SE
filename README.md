# 🍽️ DailyDish

Eine smarte Rezept-App die täglich ein personalisiertes Rezept vorschlägt – basierend auf den Ernährungspräferenzen des Nutzers.

> Uni-Projekt · HAW Hamburg · Medieninformatik · Software Engineering · 2026

(Readme mithilfe von KI generiert)
---

## Projektbeschreibung

DailyDish löst ein alltägliches Problem: *"Was esse ich heute?"*. Nutzer setzen einmalig ihre Präferenzen (z.B. vegetarisch, asiatisch, schnell) und erhalten täglich einen passenden Rezeptvorschlag aus der Datenbank.

Der Kern der Anwendung ist ein **Tag-Matching-Algorithmus** auf Basis des Jaccard-Koeffizienten, der Nutzer-Tags mit Rezept-Tags vergleicht und das am besten passende Rezept auswählt. Dabei werden **Pflicht-Tags** (z.B. Allergien, Diätvorschriften) hart gefiltert – ein Rezept das nicht alle Pflicht-Tags erfüllt wird nie vorgeschlagen, unabhängig vom Score.

---

## Tech-Stack

| Komponente | Technologie |
|---|---|
| Backend / API | Python · FastAPI |
| Datenbank | SQLite (via SQLAlchemy ORM) |
| Validierung | Pydantic |
| Testing | pytest |
| Frontend | HTML · JavaScript |
| Versionskontrolle | Git · GitHub |
| Projektmanagement | GitHub Projects (SCRUM) |

---

## Projektstruktur

```
DailyDish_SE/
├── main.py                     # Einstiegspunkt, FastAPI App
├── database.py                 # Datenbankverbindung, SQLAlchemy Session
├── seed.py                     # Beispieldaten für Entwicklung
├── conftest.py                 # pytest Konfiguration
│
├── models/
│   ├── user.py                 # SQLAlchemy Modell: User
│   ├── recipe.py               # SQLAlchemy Modell: Recipe
│   ├── tag.py                  # SQLAlchemy Modell: Tag
│   ├── suggestion_history.py   # SQLAlchemy Modell: Suggestion History
│   └── join_tables.py          # Many-to-Many Join-Tabellen
│
├── schemas/
│   ├── userSchema.py           # Pydantic Schemas: User
│   ├── recipeSchem.py          # Pydantic Schemas: Recipe
│   └── tagSchema.py            # Pydantic Schemas: Tag
│
├── routers/
│   ├── userRout.py             # Endpunkte: /user
│   ├── recipeRout.py           # Endpunkte: /recipes
│   ├── tagRout.py              # Endpunkte: /tag
│   ├── favouriteRout.py        # Endpunkte: /favourites
│   └── suggestionRout.py       # Endpunkte: /suggestions
│
├── static/
│   ├── css/   
|   |   └── style.css           # Stylesheet  
|   ├── images/recipes 
|   |   └── ~Pictures~          # Recipe Pictures
│   └── js/   
|       ├── app.js              # General Scripts for the App
|       ├── choose-tags.js      # Script for Choose-Tags Page
|       ├── dashboard.js        # Scripts for the Dashboard
|       └── favourites.js       # Scripts for the Favourites Page
|
├── templates/
│   ├── base.html               # Header
│   ├── choose_tags.html        # Choose-Tags Page
│   ├── dashboard               # Dashboard Page
│   ├── favourites.html         # Favourites Page
│   ├── login.html              # Login Page
│   └── signup.html             # Signup Page
│
├── schemas/
│   ├── userSchema.py           # Pydantic Schemas: User
│   ├── recipeSchem.py          # Pydantic Schemas: Recipe
│   └── tagSchema.py            # Pydantic Schemas: Tag
│
└── tests/
    ├── __init__.py
    ├── test_onboarding_redirect.py   # Unit-Tests fürs Frontend
    └── test_tag_matcher.py     # Unit-Tests für den Algorithmus
```

---

## Setup & Installation

### Voraussetzungen

- Python 3.10+
- pip

### 1. Repository klonen

```bash
git clone https://github.com/finnwelker/DailyDish_SE.git
cd DailyDish_SE
```

### 2. Abhängigkeiten installieren

```bash
pip install fastapi uvicorn sqlalchemy pydantic pytest python-multipart jinja2 
```

### 3. Datenbank initialisieren & Beispieldaten laden

```bash
python seed.py
```

Erstellt `dailydish.db` mit Beispiel-Rezepten, Tags und Nutzern.

### 4. Server starten

```bash
python -m uvicorn main:app --reload
```

Die API läuft nun unter `http://127.0.0.1:8000`.

Nun per http://127.0.0.1:8000 auf die Startseite und mit Signup ein Profil erstellen (oben rechts). Danach einloggen und Anweisungen folgen!

---

## API-Dokumentation

FastAPI generiert automatisch eine interaktive Dokumentation:

| URL | Beschreibung |
|---|---|
| `http://127.0.0.1:8000/docs` | Swagger UI – interaktives Testen |
| `http://127.0.0.1:8000/redoc` | ReDoc – lesbare Dokumentation |

### Endpunkte

#### Rezepte
| Methode | Endpunkt | Beschreibung |
|---|---|---|
| `GET` | `/recipes` | Alle Rezepte abrufen |
| `GET` | `/recipes/{recipe_id}` | Einzelnes Rezept abrufen |
| `POST` | `/recipes` | Neues Rezept anlegen |

#### Nutzer
| Methode | Endpunkt | Beschreibung |
|---|---|---|
| `GET` | `/user` | Alle Nutzer abrufen |
| `GET` | `/user/{user_id}` | Einzelnen Nutzer abrufen |
| `GET` | `/user/{user_id}/tags` | Tags von einzelnem Nutzer abrufen |
| `POST` | `/user` | Neuen Nutzer anlegen |
| `POST` | `/user{user_id}/tags/by-name/{tag_name}` | Tag für einzelnen Nutzer hinzufügen |
| `DELETE` | `/user{user_id}/tags/by-name/{tag_name}` | Tag für einzelnen Nutzer entfernen |

#### Authentifizierung
| Methode | Endpunkt | Beschreibung |
|---|---|---|
| `GET` | `/signup` | Registrierungs-Formular aufrufen |
| `GET` | `/login` | Login-Formular aufrufen |
| `GET` | `/choose-tags` | Tag-Wahl aufrufen |
| `GET` | `/logout` | Logout aufrufen |
| `POST` | `/signup` | Nutzer registrieren |
| `POST` | `/login` | Nutzer einloggen |
| `POST` | `/choose-tags` | Tag-Wahl speichern |


#### Tags
| Methode | Endpunkt | Beschreibung |
|---|---|---|
| `GET` | `/tag` | Alle verfügbaren Tags abrufen |
| `GET` | `/tag/{tag_id}` | Einzelnes Tag abfrufen |
| `POST` | `/tag` | Neuen Tag anlegen |

#### Vorschlag
| Methode | Endpunkt | Beschreibung |
|---|---|---|
| `GET` | `/suggestions/{user_id}` | Tagesrezept für Nutzer abrufen, alternativ mit Boolean "skip" um das Rezept zu überspringen |

#### Favoriten
| Methode | Endpunkt | Beschreibung |
|---|---|---|
| `GET` | `/user/{user_id}/favourites` | Favouriten-Liste des Nutzers aufrufen |
| `POST` | `/user/{user_id}/favourites/{recipe_id}` | Rezept zur Favoriten-Liste des Nutzers hinzufügen |
| `DELETE` | `/user/{user_id}/favourites/{recipe_id}` | Rezept von der Favoriten-Liste des Nutzers entfernen |

---

## Algorithmus

Der Vorschlagsalgorithmus läuft in zwei Schritten:

**Schritt 1 – Harte Filterung**
Rezepte die nicht alle Pflicht-Tags des Nutzers erfüllen werden vollständig ausgeschlossen. Pflicht-Tags sind Einschränkungen wie Allergien oder Diätvorschriften (`is_required=True`), z.B. `vegetarisch`, `halal`, `laktoseintolerant`.

**Schritt 2 – Jaccard-Scoring**
Aus den verbleibenden Rezepten wird das beste anhand des Jaccard-Koeffizienten ausgewählt:

```
Score = |User-Tags ∩ Rezept-Tags| / |User-Tags ∪ Rezept-Tags|
```

Ein Score von `1.0` bedeutet perfekte Übereinstimmung, `0.0` bedeutet keine gemeinsamen Tags. Das Rezept mit dem höchsten Score wird zurückgegeben.

---

## Tests

```bash
python -m pytest tests/ -v
```

Die Unit-Tests decken folgende Fälle ab:

- Perfekte Tag-Übereinstimmung
- Keine Übereinstimmung
- Teilweise Übereinstimmung (Jaccard-Berechnung)
- Leere Tag-Mengen
- Pflicht-Tags filtern unpassende Rezepte aus
- Nutzer nicht gefunden
- Keine gültigen Rezepte verfügbar
- etc.

---

## Vorgehensmodell

Das Projekt wird nach **SCRUM** entwickelt mit 1,5-wöchigen Sprints. Der aktuelle Stand des Backlogs und der Sprints ist im [GitHub Projects Board](https://github.com/finnwelker/DailyDish_SE/projects) einsehbar.

**Rollen:**
- Product Owner: Jesse, Finn 
- Scrum Master: – Finn
- Developer: Finn , Jesse

---

## Mitwirkende

| Name | Rolle |
|---|---|
| Finn | Backend · Algorithmus · Dokumentation |
| Jesse | Frontend · UI/UX |
