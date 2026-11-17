from fastapi import FastAPI, Response
from typing import Optional
import taipei

app = FastAPI()

@app.get("/subway/taipei")
def get_taipei(response: Response, lineId: Optional[str] = None):
    return taipei.mrt(lineId)
