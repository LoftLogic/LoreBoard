from langchain.prompts import PromptTemplate
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)

from templates.entity_templates import generate_character_sheet

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser

import json

class ChapterMetaSheet:
    """
    Represents a review of a previous chapter or section.
    """
    def __init__(self, name: str):
        self.default_str = "To be created. Run update to get started."
        self.name = name
        self.plot_summary = self.default_str
        self.characters = self.default_str
        self.tone = self.default_str
        self.world = self.default_str
        self.themes = self.default_str
        self.viewer_enjoyment = self.default_str
        
    def update(self):
        """
        Updates the metadata of the chapter.
        Can be considered an expensive operation.
        """
        pass