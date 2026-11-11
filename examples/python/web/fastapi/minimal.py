from fastapi import FastAPI

app = FastAPI(title="Учебный API", version="1.0.0")


@app.get("/")
def root():
    return {"message": "Привет"}
