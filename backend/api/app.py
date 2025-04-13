from fastapi import FastAPI, HTTPException
from backend.pages.assistantpage import Entity, Character, Setting

app = FastAPI()

entities : list[Entity] = []

@app.post("/")
def root():
    return { "result": "Send an entity or text body" }

@app.post("/entities/{entity_type}")
def create_entity(entity_type: str, entity_data: dict):
    if entity_type not in ("Character", "Setting", "Item"):
        raise HTTPException(status_code=400, detail="Invalid type")
    if "name" not in entity_data:
        raise HTTPException(status_code=400, detail="Invalid type")
    if entity_type == "Character":
        new_entity = Character(entity_data["name"])
    elif entity_type == "Setting":
        new_entity = Setting(entity_data["name"])
    else:
        raise NotImplementedError
    
    entities.append(new_entity)
    
    return {
        "message": "Entity created",
        "entity_type": entity_type,
        "entity_data": entity_data
    }
    
@app.post("/entities/update_entity/{passage_text}")
def update_entity(passage_text: str, entity_data: dict):
    for ent in entities:
        if entity_data["name"] == ent.name:
            entity = ent
