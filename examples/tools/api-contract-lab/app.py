from fastapi import FastAPI, HTTPException
from psycopg import connect
from pydantic import BaseModel

app = FastAPI()


class Book(BaseModel):
    id: int
    title: str


@app.get("/books/{book_id}")
def read_book(book_id: int) -> Book:
    with connect(connect_timeout=5) as conn:
        row = conn.execute(
            "SELECT id, title FROM books WHERE id = %s",
            (book_id,),
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Book not found")

    return Book(id=row[0], title=row[1])
