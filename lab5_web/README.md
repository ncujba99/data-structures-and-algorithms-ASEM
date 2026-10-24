# Lab 5, Task 1 as a real web app

[Lab 5, Task 1](../lab5/docs/zadanie1_poezda.md) builds a train-station information desk on a hand-written binary search tree. This folder solves the same task the way it is done at work: a React frontend, a REST API, and a relational database, each in its own container.

It makes two points:

1. **A relational database does far more than the lab's tree.** Data lives in several related tables, the database enforces the rules between them, and any new question is one query, not a new traversal function.
2. **Inside, it is still the same tree.** PostgreSQL stores every primary key, UNIQUE constraint and index as a **B+-tree**: a balanced search tree whose nodes hold hundreds of keys and are sized to a disk page. The *Под капотом* tab lists these trees and shows the plans that walk them.

```
╭──────────────╮      ┌──────────────────────┐      ┌──────────────────────┐      ┌──────────────────────┐
│   browser    │ ───► │  frontend  :5173     │ ───► │  backend  :8000      │ ───► │  db  PostgreSQL 16   │
│              │      │  React + Vite        │ /api │  FastAPI, SQLAlchemy │ SQL  │  4 tables            │
│              │ ◄─── │  forwards /api/* to  │ ◄─── │  Alembic migrations  │ ◄─── │  11 B+-tree indexes  │
╰──────────────╯      │  the backend         │ JSON │  run on start        │      │                      │
                      └──────────────────────┘      └──────────────────────┘      └──────────────────────┘
```

## Data model

```
┌───────────────────┐        ┌─────────────────────────┐        ┌──────────────────────────┐
│ countries         │        │ cities                  │        │ trains                   │
│ code  PK  ("MD")  │ 1    N │ id            PK        │ 1    N │ number          PK       │
│ name  UNIQUE      │◄───────│ name          UNIQUE    │◄───────│ destination_id  FK       │
└───────────────────┘        │ country_code  FK, NULL  │        │ departure                │
                             └─────────────────────────┘        └──────────────────────────┘
                                          ▲ 1                                ▲ 1
                                          │ N   ┌─────────────────────────┐  │ N
                                          └─────│ train_stops             │──┘
                                                │ train_number  PK, FK    │  ON DELETE CASCADE
                                                │ stop_no       PK        │
                                                │ city_id       FK        │
                                                └─────────────────────────┘
```

- **countries.** The key is the ISO 3166 code (`MD`, `RO`, …): short, well known and never changing, so it works as a natural primary key. `cities.country_code` refers to it.
- **cities.** Each city is stored once. Trains refer to it by `id`, so a city's name exists in exactly one row.
- **trains.** The lab's record. `number` is the key field, as in the lab; `destination_id` is the final station.
- **train_stops.** The intermediate stations of each train, in order. This is a many-to-many link: a train has many stops, a city is a stop for many trains. Deleting a train deletes its stops (`ON DELETE CASCADE`).

## Why a relational database

| | Lab 5 tree | Here | Try it |
|---|---|---|---|
| **One fact, one place** | the station name is copied into every `Train`; renaming means visiting every node, and a typo creates a new station | the name is one row in `cities`; trains store its `id` | *Города* → rename Киев; every route changes at once |
| **References stay valid** | nothing links a train to a real station | foreign keys: a train cannot point to a missing city, and a city in use cannot be deleted | *Города* → delete Киев: refused |
| **Rules for every client** | checks live in `console.py`; other code can skip them | `CHECK`, `UNIQUE`, `NOT NULL` live in the table, so the UI, `psql` and any other program are held to them | add train 50 twice: `409` |
| **All or nothing** | a crash halfway through an update leaves the tree half-changed | a transaction: the train and all its stops are saved, or none of them | add a train with the same stop twice: no train appears |
| **New questions** | each one is a new traversal function | one query: filters, ranges, `JOIN`, `GROUP BY` | *Поиск поездов* → from Бельцы to Киев: the order of stops decides; *Расписание* → filter by city and time range; *Отчёты* |
| **Related data** | the tree holds one kind of record | countries, cities, trains and stops, with links between them | the *Маршрут* column |
| **Persistence, many users** | in memory, one user, gone on exit | on disk, survives restarts, many users at once | `docker compose restart` |
| **Changing the structure** | rewrite the program | migrations convert the existing data | see [Database migrations](#database-migrations-alembic) |

## …and inside it is the same tree

| Lab 5, Task 1 (`zadanie1_poezda.py`) | PostgreSQL |
|---|---|
| `Node` with `left` / `right` pointers | B+-tree page with hundreds of keys and child pointers |
| tree ordered by the key field (train number) | `trains_pkey`, created by `PRIMARY KEY (number)` |
| search: walk down from the root, O(height) | `Index Scan using trains_pkey` |
| inorder traversal prints the trains sorted | `ORDER BY number` reads `trains_pkey` in order; leaves are linked left to right |
| part of the inorder traversal, from key a to key b | `departure BETWEEN a AND b` uses `trains_departure_idx` |
| search by station: traverse everything, O(n) | another tree, `trains_destination_id_idx`, ordered by city |
| condition the tree is not ordered by: traverse everything | `Seq Scan`, e.g. `extract(minute FROM departure) = 0` |
| plain BST: sorted input makes it a list | B+-tree splits and merges pages and stays balanced |
| delete through the inorder predecessor | `DELETE`; the page is updated, and empty pages are reclaimed by VACUUM |

There are 11 such trees in this database: one per primary key, one per UNIQUE constraint, and one per explicit index. PostgreSQL does **not** index foreign keys by itself, so the models declare `index=True` on them, which creates `cities_country_code_idx`, `trains_destination_id_idx` and `train_stops_city_id_idx` explicitly. Without them, "trains to this city" and "may this city be deleted?" would read the whole table.

With 9 demo rows PostgreSQL reads the whole table, because that is cheaper than opening an index. In *Под капотом*, press **Заполнить номера 1…9999** and the plans switch to the trees:

```
SELECT * FROM trains WHERE number = 50
Index Scan using trains_pkey on trains                     ← walk down one tree

SELECT t.* FROM trains t JOIN cities c ON c.id = t.destination_id WHERE c.name = 'Москва'
Nested Loop
  ->  Seq Scan on cities c                                 ← 10 cities: a scan is cheaper
  ->  Bitmap Heap Scan on trains t
        ->  Bitmap Index Scan on trains_destination_id_idx ← for each city found, search the second tree

SELECT * FROM trains WHERE departure BETWEEN '08:00' AND '12:00'
Bitmap Heap Scan on trains
  ->  Bitmap Index Scan on trains_departure_idx            ← a key range: part of an inorder traversal

SELECT * FROM trains WHERE extract(minute FROM departure) = 0
Seq Scan on trains                                         ← no tree is ordered by "minute": read all 9 999 rows
```

Every trains index is then 2 levels high. A binary tree needs at least 14 levels for 9 999 keys.

## Running

You need Docker with Compose (Docker Desktop, or Podman with `podman compose`).

```sh
cd lab5_web
docker compose up --build
```

| Open | What it is |
|---|---|
| http://localhost:5173 | the app |
| http://localhost:8000/docs | the API, interactive (generated by FastAPI) |

Stop with `Ctrl+C`. `docker compose down` removes the containers; the data stays in `lab5_web/pgdata/`, a folder next to `docker-compose.yml` (git-ignored). To start from an empty database, stop the stack and delete that folder: the next start runs the migration and loads the demo data.

The database password defaults to `station`. Set `POSTGRES_PASSWORD` to change it, for example in a `.env` file next to `docker-compose.yml`.

With Podman, add `--force-recreate` after changing the code (`podman compose up -d --build --force-recreate`). Docker Compose recreates changed containers by itself.

## Project layout

```
lab5_web/
├── docker-compose.yml               ← the three services
├── pgdata/                          ← the database files, created on first start (git-ignored)
├── backend/
│   ├── Dockerfile                   ← runs `alembic upgrade head`, then uvicorn
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── migrations/
│   │   ├── env.py                   ← compares models.py with the database
│   │   └── versions/                ← generated by `alembic revision --autogenerate`
│   └── app/
│       ├── main.py                  ← creates the app, plugs in the routers, loads demo data into an empty database
│       ├── models.py                ← the schema as SQLAlchemy classes; the migrations are built from it
│       ├── db.py                    ← engine, one session per request, database errors → HTTP answers, EXPLAIN
│       ├── demo_data.py             ← the lab's 9 trains, as plain Python data
│       └── routers/                 ← one per resource: its Pydantic schemas and its routes, one Swagger section each
│           ├── common.py            ← shared field types, the error model
│           ├── health.py            ← first in the app and in /docs
│           ├── trains.py
│           ├── cities.py
│           ├── countries.py
│           ├── reports.py
│           ├── internals.py         ← EXPLAIN, index list
│           └── demo.py              ← reset the demo data, bulk fill
└── frontend/
    ├── Dockerfile                   ← Vite dev server
    ├── package.json
    ├── vite.config.js               ← forwards /api to the backend
    ├── index.html
    └── src/
        ├── main.jsx
        ├── App.jsx                  ← tabs; loads cities and countries for all of them
        ├── api.js                   ← one function per API call
        ├── style.css
        ├── components/              ← Toast, SqlBlock
        └── tabs/                    ← SearchTab (passenger search), TrainsTab (schedule), CitiesTab, CountriesTab, ReportsTab, InternalsTab
```

## API

Interactive docs: http://localhost:8000/docs (Swagger) and http://localhost:8000/redoc. Every endpoint shows its response shape, its errors and an example request; the examples use the city ids of the demo data, so run `POST /api/demo/reset/` first. All paths end with `/`; without it FastAPI answers with a redirect.

| Method and path | Does | Lab menu item |
|---|---|---|
| `GET /api/health/` | `{"status": "ok"}` when the database answers | — |
| `GET /api/trains/` | trains sorted by number, with destination, country and stops. Filters: `city_id`, `match` (`to`: ending there, the default; `via`: passing through as an intermediate stop; `both`), `time_from`, `time_to`, `limit` (200, at most 1000) | 2, 4 |
| `GET /api/trains/search/` | the passenger search: `to_id` (required), `from_id` (a stop before it; omit for our station), `time_from`, `time_to`. Sorted by departure | 4 |
| `GET /api/trains/{number}/` | one train, `404` if missing | 3 |
| `POST /api/trains/` | `{"number": 15, "destination_id": 3, "departure": "07:05", "stops": [2]}`, saved in one transaction | 1 |
| `DELETE /api/trains/{number}/` | delete with its stops; returns the deleted train, so the client can undo | 5, 7 |
| `GET` / `POST /api/cities/`, `GET` / `PATCH` / `DELETE /api/cities/{id}/` | the city list (with train counts), add, rename or change country, delete | — |
| `GET` / `POST /api/countries/`, `GET` / `PATCH` / `DELETE /api/countries/{code}/` | the same for countries | — |
| `GET /api/reports/countries/`, `/api/reports/cities/` | trains per country; busiest cities. Each answer includes the Python query and its SQL | — |
| `GET /api/indexes/` | every B-tree index with its height and size | 6 |
| `GET /api/explain/` | the four searches above: Python query, SQL, plan | 6 |
| `POST /api/demo/bulk/`, `/api/demo/reset/` | fill numbers 1…9999 with random trains; back to the demo data | 8 |

The database has the last word on the rules. When it refuses a change, [db.py](backend/app/db.py) turns the constraint name into an answer: `409` for a duplicate or a row still in use, `422` for a missing reference or a failed check.

## Code: SQLAlchemy, Pydantic, Alembic

There is no SQL written by hand in the backend. Each layer is described once, in Python:

| Layer | File | Does |
|---|---|---|
| Tables | [models.py](backend/app/models.py) | SQLAlchemy classes: columns, keys, constraints, indexes, relationships. `Train.stops` is an ordered list (`ordering_list` numbers the stops) |
| Queries | [routers/](backend/app/routers/) | `select(Train).where(...)`, `Train.stops.any(...)`, `exists()`, `func.count()`; SQLAlchemy writes the SQL |
| JSON | [routers/](backend/app/routers/) | Pydantic models next to their routes; response models read ORM objects (`from_attributes`), so a route returns a `Train` and FastAPI sends its JSON |
| Migrations | [migrations/versions/](backend/migrations/versions/) | generated by Alembic from the models |

Every route gets a session that is one transaction: committed when the route returns, rolled back if it raises. The *Отчёты* and *Под капотом* tabs show each query three ways: the Python that builds it, the SQL SQLAlchemy makes of it, and PostgreSQL's plan.

Two PostgreSQL commands have no SQLAlchemy construct, `EXPLAIN` and `ANALYZE` (and `TRUNCATE` for the demo reset). [db.py](backend/app/db.py) adds them with SQLAlchemy's compiler extension, so `session.execute(Explain(query))` works for any query.

## Database migrations (Alembic)

The schema is never changed by hand. Alembic compares [models.py](backend/app/models.py) with the database and writes the difference as a migration file in `backend/migrations/versions/`. On every start the backend runs `alembic upgrade head`, which applies the files this database has not seen yet; the applied version is stored in table `alembic_version`. Data is not a migration: on startup the app loads the demo data if the database is empty.

| Revision | Change |
|---|---|
| [0001](backend/migrations/versions/0001_initial_schema.py) | generated from the models: the `pageinspect` extension (through `alembic_utils`), 4 tables, their keys, constraints and indexes |

```sh
docker compose exec backend alembic current        # 0001 (head)
docker compose exec backend alembic check          # "No new upgrade operations detected": models and database agree
```

To change the schema, for example to add a platform number:

1. Edit the model: `platform: Mapped[int | None]` in `Train`.
2. Generate the migration on your machine, against the running database (port 5432 is published for this):
   ```sh
   cd backend
   pip install -r requirements.txt
   DATABASE_URL=postgresql://station:station@localhost:5432/station \
       alembic revision --autogenerate -m "add platform"
   ```
3. Read the generated file: autogenerate does not see everything, for example a renamed column looks like a dropped one and a new one.
4. `docker compose up --build`: the backend applies it on start.

A database created by the earlier, hand-written migrations (0001 … 0004) has a version Alembic no longer knows; start it fresh: `docker compose down`, delete `pgdata/`, start again.

## Looking inside with psql

```sh
docker compose exec db psql -U station -d station
```
```sql
\d trains                                         -- columns, keys, indexes, foreign keys
EXPLAIN SELECT * FROM trains WHERE number = 50;
SELECT level + 1 AS height FROM bt_metap('trains_pkey');
DROP INDEX trains_departure_idx;                  -- the time-range search becomes a Seq Scan
EXPLAIN SELECT * FROM trains WHERE departure BETWEEN '08:00' AND '12:00';
```

Deleting `pgdata/` (with the stack stopped) brings the dropped index back on the next start.

## What a production deployment would add

This setup is for running on your own machine. In production you would also:

- serve the frontend as built static files (`npm run build` → `dist/`) from a CDN or a web server, instead of the Vite dev server;
- run migrations as a separate one-off job before deploying, not inside every API container;
- give the API its own database role with only the rights it needs, and keep passwords in a secret store;
- add login, HTTPS, backups, logs and monitoring;
- drop the `pageinspect` extension and the `/api/demo/*`, `/api/explain/` and `/api/indexes/` endpoints, which exist only to show the internals.
