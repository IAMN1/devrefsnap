# Принять форму и загруженные файлы

Откройте страницу, если запрос содержит multipart-форму с одним или несколькими файлами.
Пример измеряет синтетические файлы и не сохраняет пользовательские данные.

| Задача | Приём | Пример |
| --- | --- | --- |
| Принять форму | `Form` | [Полный uploads.py](#формы-и-загрузка-файлов) |
| Ограничить прочитанный файл | `UploadFile.read` порциями | [Полный uploads.py](#формы-и-загрузка-файлов) · [Карточка](recipes.md#формы-и-загрузка-файлов) |
| Проверить размер и отказ | Синтетические bytes и ответ 413 | [Полные тесты](testing-lab.md#файлы-и-middleware) |

[Карточки HTTP](recipes.md) · [Справочник FastAPI](README.md) · [Проверки](testing.md)

Уровень: средний.
Используйте Python 3.14.
В отдельном окружении выполните `python -m pip install 'fastapi==0.162.0' 'uvicorn[standard]' 'python-multipart==0.0.33'`.

## Формы и загрузка файлов

Сохраните самостоятельный пример в файле `uploads.py`:

<!-- example: uploads.py -->
```python
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
```

```bash
uvicorn uploads:app --reload
```

Для проверки загрузите существующий учебный файл.
`@` в curl означает чтение локального файла:

```bash
curl -F 'username=alice' http://127.0.0.1:8000/form
curl -F 'file=@uploads.py' http://127.0.0.1:8000/upload
curl -F 'files=@uploads.py' -F 'files=@uploads.py' http://127.0.0.1:8000/uploads
```

Первый результат содержит имя из формы.
Второй результат содержит имя и размер файла.
Третий результат содержит список из двух результатов.
Ограничение в обработчике проверяет прочитанное содержимое одного файла.
Это ограничение не проверяет полный размер HTTP-запроса до multipart-парсинга.
Задайте общий лимит тела также на сервере или прокси.
Задайте лимит числа файлов также на сервере или прокси.
Имя и MIME-тип присылает клиент.
Пример не сохраняет файлы.
Пример не проверяет фактический формат файлов.
JSON body и multipart body — разные форматы одного запроса.

Источники: [файлы](https://fastapi.tiangolo.com/tutorial/request-files/), [формы и файлы](https://fastapi.tiangolo.com/tutorial/request-forms-and-files/).
