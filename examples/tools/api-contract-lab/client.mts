type Book = { id: number; title: string };

async function getJson(id: number, expectedStatus: number): Promise<unknown> {
  const path = `/books/${id}`;
  const response = await fetch(`http://app:8000${path}`, {
    signal: AbortSignal.timeout(5000),
  });
  if (response.status !== expectedStatus) {
    throw new Error(`GET ${path}: expected HTTP ${expectedStatus}, got ${response.status}`);
  }
  return response.json();
}

function parseBook(data: unknown): Book {
  if (
    typeof data !== "object" ||
    data === null ||
    !("id" in data) ||
    typeof data.id !== "number" ||
    !Number.isInteger(data.id) ||
    !("title" in data) ||
    typeof data.title !== "string"
  ) {
    throw new Error("GET /books/1: expected a JSON object with integer id and string title");
  }
  return { id: data.id, title: data.title };
}

const book = parseBook(await getJson(1, 200));
if (book.id !== 1 || book.title !== "The Hobbit") {
  throw new Error(`GET /books/1: unexpected book ${JSON.stringify(book)}`);
}
console.log(`OK GET /books/1 -> 200 ${book.title}`);

const missing = await getJson(999, 404);
if (
  typeof missing !== "object" ||
  missing === null ||
  !("detail" in missing) ||
  missing.detail !== "Book not found"
) {
  throw new Error('GET /books/999: expected JSON with detail "Book not found"');
}
console.log("OK GET /books/999 -> 404 Book not found");
