from fastapi import FastAPI, Response

app = FastAPI()

@app.get("/subway/taipei")
def seoul(response: Response, lineId: Optional[str] = None):
    response.headers['Access-Control-Allow-Origin'] = '*'

    internalIds = {
        'BR': 'NH',
        'R': 'RG',
        'G': 'GR',
        'O': 'OR',
        'BL': 'BL',
        'Y': 'YL',
    };
    if not internalIds.get(lineId): return []

    return []
