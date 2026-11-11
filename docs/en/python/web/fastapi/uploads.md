<a id="принять-форму-и-загруженные-файлы"></a>
# Accept a form and uploaded files

[Русский](../../../../ru/python/web/fastapi/uploads.md)

Use this page when a request contains a multipart form with one or several files.
The example measures synthetic files without storing user data.

| Task | Technique | Example |
| --- | --- | --- |
| Accept a form | `Form` | [Complete uploads.py](#forms-and-file-uploads) |
| Limit file content read | Read in chunks with `UploadFile.read` | [Complete uploads.py](#forms-and-file-uploads) · [Card](recipes.md#forms-and-file-uploads) |
| Check size and rejection | Synthetic bytes and a 413 response | [Complete tests](testing-lab.md#files-and-middleware) |

[HTTP cards](recipes.md) · [FastAPI reference](README.md) · [Checks](testing.md)

Intermediate level.
Use Python 3.14.
In a separate environment, run `python -m pip install 'fastapi==0.162.0' 'uvicorn[standard]' 'python-multipart==0.0.33'`.

<a id="формы-и-загрузка-файлов"></a>
## Forms and file uploads

Save the standalone example in `uploads.py`.

[`uploads.py`](../../../../../examples/python/web/fastapi/uploads.py)

```bash
uvicorn uploads:app --reload
```

Upload an existing practice file to check the example.
In curl, `@` reads a local file.

```bash
curl -F 'username=alice' http://127.0.0.1:8000/form
curl -F 'file=@uploads.py' http://127.0.0.1:8000/upload
curl -F 'files=@uploads.py' -F 'files=@uploads.py' http://127.0.0.1:8000/uploads
```

The first result contains the name from the form.
The second result contains the file's name and size.
The third result contains a list of two results.
The handler's limit checks the content read from one file.
This limit does not check the complete HTTP request size before multipart parsing.
Set a total body limit on the server or proxy as well.
Set a file-count limit on the server or proxy as well.
The client supplies the filename and MIME type.
The example does not save files.
The example does not verify the actual file format.
JSON bodies and multipart bodies are different formats for a request.

Sources include [files](https://fastapi.tiangolo.com/tutorial/request-files/) and [forms and files](https://fastapi.tiangolo.com/tutorial/request-forms-and-files/).
