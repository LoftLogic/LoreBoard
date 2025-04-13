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
        self.name = name
        self.reset()
        
    def reset(self):
        self.default_str = "To be created. Run update to get started."
        self.plot_summary = self.default_str
        self.characters = self.default_str
        self.tone = self.default_str
        self.world = self.default_str
        self.themes = self.default_str
        self.viewer_enjoyment = self.default_str
        self.initialized_flag = False
        
    def update(self, chapter: str):
        """
        Updates the metadata of the chapter.
        Can be considered an expensive operation.
        """
        self.initialized_flag = True
        template: ChatPromptTemplate = generate_character_sheet(chapter)
        
        llm = ChatOpenAI(model='gpt-4o')
        parser = JsonOutputParser()
        
        llm_chain = template | llm | parser
                
        print(chapter)
        
        return llm_chain.invoke({"chapter": chapter})