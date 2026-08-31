from fastapi import FastAPI, Response

app = FastAPI()

@app.get("/subway/taipei")
def seoul(response: Response, lineId: Optional[str] = None):
    response.headers['Access-Control-Allow-Origin'] = '*'
    
    return []
