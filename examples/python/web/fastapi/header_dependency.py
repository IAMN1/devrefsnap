from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException

app = FastAPI()


def verify_client(x_client: Annotated[str, Header()]):
    if x_client != "training-client":
        raise HTTPException(400, "Неизвестный клиент")


@app.get("/checked", dependencies=[Depends(verify_client)])
def checked():
    return {"checked": True}
