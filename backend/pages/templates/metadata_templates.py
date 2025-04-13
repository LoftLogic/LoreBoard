from langchain.prompts import PromptTemplate
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)

def generate_chapter_metadata(passage: str, last_summaries: list[str]) -> ChatPromptTemplate:
    """
    Generates approprite metadata for a chapter.
    """
    
    template_str = """
    # Prompt
    Objective: Your to act as a creative writing assistant focused on chapter analysis. Your given a chapter, and summarization information of previous chapters.
    First read the summarization information for context, then, go through the given chapter and record notes.
    """