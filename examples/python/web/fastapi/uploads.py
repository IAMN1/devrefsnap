from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, UploadFile

app = FastAPI()
MAX_BYTES = 1024 * 1024


@app.post("/form")
async def read_form(username: Annotated[str, Form(min_length=1)]):
    return {"username": username}


async def measure(file: UploadFile):
    size = 0
    try:
        while chunk := await file.read(64 * 1024):
            size += len(chunk)
            if size > MAX_BYTES:
                raise HTTPException(413, "Файл больше 1 MiB")
        return {"filename": file.filename, "size": size}
    finally:
        await file.close()


@app.post("/upload")
async def upload(file: Annotated[UploadFile, File()]):
    return await measure(file)


@app.post("/uploads")
async def uploads(files: Annotated[list[UploadFile], File()]):
    return [await measure(file) for file in files]
