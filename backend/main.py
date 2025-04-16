from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import entities, aliases
from app.core.config import settings

app = FastAPI(title="LoreBoard API", description="API for the LoreBoard creative writing platform")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For MVP, we'll allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(entities.router, prefix="/api")
app.include_router(aliases.router, prefix="/api")

@app.get("/")
def health_check():
    return {"status": "healthy", "message": "LoreBoard API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)