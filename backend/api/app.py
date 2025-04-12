from fastapi import FastAPI, HTTPException
from backend.pages.assistantpage import Entity

app = FastAPI()

entities : list[Entity] = []

@app.post("/")
def root():
    return { "result": "Send an entity or text body" }

@app.post("/entities/{entity_type}")
def create_entity(entity_type: str):
    if entity_type not in ("Character", "Place", "Item"):
        raise HTTPException(status_code=400, detail="Invalid type")
    