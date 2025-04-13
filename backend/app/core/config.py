import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class Settings(BaseSettings):
    PROJECT_NAME: str = "LoreBoard"
    API_V1_STR: str = "/api"
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/loreboard")
    
    # OpenAI API settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    
    # Text context settings
    CONTEXT_PARAGRAPH_LIMIT: int = 2  # Number of paragraphs to consider on each side
    
    class Config:
        case_sensitive = True

settings = Settings()