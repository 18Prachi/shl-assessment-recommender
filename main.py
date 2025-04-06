from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from model_utils import get_top_matches
import trafilatura
import requests

app = FastAPI()

class QueryInput(BaseModel):
    query: str = None
    url: str = None

@app.post("/recommend")
def recommend(input_data: QueryInput):
    if not input_data.query and not input_data.url:
        raise HTTPException(status_code=400, detail="Provide either a query or a URL.")

    if input_data.url:
        downloaded = trafilatura.fetch_url(input_data.url)
        text = trafilatura.extract(downloaded)
        if not text:
            raise HTTPException(status_code=400, detail="Failed to extract content from URL.")
        query = text
    else:
        query = input_data.query

    recommendations = get_top_matches(query)
    return {"results": recommendations}
