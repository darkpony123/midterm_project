# Library API

Simple REST API for managing books. Backend is FastAPI (Python), database is PostgreSQL. Everything runs in Docker.

## Project structure

```
library-api/
├── app/
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── docker-compose.yml
├── .env.example
├── postman_collection.json
└── README.md
```

## How to run

1. Copy `.env.example` to `.env` (or use the provided `.env`)
2. Run:
```
docker compose up --build
```
3. API is available at `http://localhost:8000`
4. Swagger UI: `http://localhost:8000/docs`

Stop: `docker compose down`. Data stays in the `pgdata` volume. To remove data too: `docker compose down -v`.

## Services

| Service | Image | Port | Description |
|---|---|---|---|
| api | built from `app/Dockerfile` | 8000 | FastAPI backend |
| db | postgres:16 | internal only | PostgreSQL database |

Both services are on the `library_net` network. The API connects to the database using the hostname `db` (service name).

## Environment variables

| Variable | Description |
|---|---|
| POSTGRES_DB | Database name |
| POSTGRES_USER | Database user |
| POSTGRES_PASSWORD | Database password |
| DB_HOST | Database host (service name `db`) |
| DB_PORT | Database port |
| APP_PORT | Port on host machine for the API |

## API documentation

Book object:
```json
{ "id": 1, "title": "Clean Code", "author": "Robert Martin", "year": 2008 }
```

| Method | Endpoint | Description | Success | Errors |
|---|---|---|---|---|
| GET | `/books` | List all books | 200 | |
| GET | `/books/{id}` | Get book by ID | 200 | 404 |
| POST | `/books` | Create a book | 201 | 422 |
| PUT | `/books/{id}` | Update a book | 200 | 404, 422 |
| DELETE | `/books/{id}` | Delete a book | 200 | 404 |

### POST /books and PUT /books/{id}
Request body:
```json
{ "title": "Clean Code", "author": "Robert Martin", "year": 2008 }
```
`title` and `author` are required, `year` is optional. Returns the saved book.

### DELETE /books/{id}
Response:
```json
{ "message": "Book 1 deleted" }
```

### 404 response
```json
{ "detail": "Book not found" }
```

## Postman

Import `postman_collection.json` into Postman. The `baseUrl` variable is `http://localhost:8000`. The "Create book" request saves the new id into `bookId`, so run it first.
