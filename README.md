# 🍽️ DailyDish

Eine smarte Rezept-App die täglich ein personalisiertes Rezept vorschlägt – basierend auf den Ernährungspräferenzen des Nutzers.

> Uni-Projekt · HAW Hamburg · Medieninformatik · Software Engineering · 2026

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
├── main.py                  # Einstiegspunkt, FastAPI App
├── database.py              # Datenbankverbindung, SQLAlchemy Session
├── seed.py                  # Beispieldaten für Entwicklung
├── conftest.py              # pytest Konfiguration
│
├── models/
│   ├── user.py              # SQLAlchemy Modell: User
│   ├── recipe.py            # SQLAlchemy Modell: Recipe
│   ├── tag.py               # SQLAlchemy Modell: Tag
│   └── join_tables.py       # Many-to-Many Join-Tabellen
│
├── schemas/
│   ├── userSchema.py        # Pydantic Schemas: User
│   ├── recipeSchem.py       # Pydantic Schemas: Recipe
│   └── tagSchema.py         # Pydantic Schemas: Tag
│
├── routers/
│   ├── userRout.py          # Endpunkte: /user
│   ├── recipeRout.py        # Endpunkte: /recipes
│   ├── tagRout.py           # Endpunkte: /tag
│   └── suggestionRout.py    # Endpunkte: /suggestions
│
├── services/
│   └── tag_matcher.py       # Algorithmus: Jaccard-Matching
│
└── tests/
    ├── __init__.py
    └── test_tag_matcher.py  # Unit-Tests für den Algorithmus
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
pip install fastapi uvicorn sqlalchemy pydantic pytest
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
| `GET` | `/recipes/{id}` | Einzelnes Rezept abrufen |
| `POST` | `/recipes` | Neues Rezept anlegen |

#### Nutzer
| Methode | Endpunkt | Beschreibung |
|---|---|---|
| `GET` | `/user` | Alle Nutzer abrufen |
| `GET` | `/user/{id}` | Einzelnen Nutzer abrufen |
| `POST` | `/user` | Neuen Nutzer anlegen |

#### Tags
| Methode | Endpunkt | Beschreibung |
|---|---|---|
| `GET` | `/tag` | Alle verfügbaren Tags abrufen |
| `POST` | `/tag` | Neuen Tag anlegen |

#### Vorschlag
| Methode | Endpunkt | Beschreibung |
|---|---|---|
| `GET` | `/suggestions/{user_id}` | Tagesrezept für Nutzer abrufen |

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

---

## Vorgehensmodell

Das Projekt wird nach **SCRUM** entwickelt mit 2-wöchigen Sprints. Der aktuelle Stand des Backlogs und der Sprints ist im [GitHub Projects Board](https://github.com/finnwelker/DailyDish_SE/projects) einsehbar.

**Rollen:**
- Product Owner: –
- Scrum Master: –
- Developer: Finn Welker, [Kommilitone]

---

## Mitwirkende

| Name | Rolle |
|---|---|
| Finn Welker | Backend · Algorithmus · Dokumentation |
| [Kommilitone] | Frontend · UI/UX |
