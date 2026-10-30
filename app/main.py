import os
from contextlib import asynccontextmanager

import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


DB_CONFIG = {
    "host": os.getenv("DB_HOST", "db"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
}


def get_conn():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # create the table on startup if it doesn't exist yet
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id SERIAL PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                author VARCHAR(200) NOT NULL,
                year INT
            )
        """)
    yield


app = FastAPI(title="Library API", lifespan=lifespan)


class Book(BaseModel):
    title: str
    author: str
    year: int | None = None


@app.get("/")
def health():
    return {"status": "ok"}


@app.get("/books")
def list_books():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM books ORDER BY id")
        return cur.fetchall()


@app.get("/books/{book_id}")
def get_book(book_id: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM books WHERE id = %s", (book_id,))
        book = cur.fetchone()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.post("/books", status_code=201)
def create_book(book: Book):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO books (title, author, year) VALUES (%s, %s, %s) RETURNING *",
            (book.title, book.author, book.year),
        )
        return cur.fetchone()


@app.put("/books/{book_id}")
def update_book(book_id: int, book: Book):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "UPDATE books SET title = %s, author = %s, year = %s WHERE id = %s RETURNING *",
            (book.title, book.author, book.year, book_id),
        )
        updated = cur.fetchone()
    if not updated:
        raise HTTPException(status_code=404, detail="Book not found")
    return updated


@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM books WHERE id = %s RETURNING id", (book_id,))
        deleted = cur.fetchone()
    if not deleted:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": f"Book {book_id} deleted"}
