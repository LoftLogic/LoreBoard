from langchain.prompts import PromptTemplate
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)

# TODO: Make relevant passages also contain data about the location of text.
def generate_character_sheet(passages: list[str], character: str, aliases: set[str]) -> ChatPromptTemplate:
    """
    Generates a character sheet for a given character.
    """
    
    aliases_copy = aliases.copy()
    
    if character in aliases_copy:
        aliases_copy.remove(character)
    
    recognition_str = ""
    
    if aliases_copy:
        recognition_str = "This character also has the names/aliases "
        for alias in aliases_copy:
            recognition_str += alias + ", "
        recognition_str = recognition_str[:-2]
    
    template_str = """
    # Prompt
    
    Objective: Your to act as a creative writing assistant, focusing on characters. 
    You will be given a set of one or more passages. Seperate passages will be seperated by '======================'
    Your job is to record information about the character {{character}}. 
    {{recognition_str}}
    The information your record should serve as brief notes on what the writer has written so far, and will be used later for reference.
    As such, recorded information should be densely informative and 
    
    You are to primarily record the following infromation about {{character}}:
    - Basic Role: Essentially, who this person is and what are their most relevant information to the story, in one or two short sentences.
    - Physical Descriptions: Such as size, hair color, facial characteristics, and any discernable physical traits.
    - Personality Descriptions: Such as their speaking style, outward demeanor, inner psycholgical complexities, and anything about the mind of the characters.
    Also record the following, if applicable. If not applicable (in the instance the character is minor or the text does not cover these), simply put 'Not Applicable'.
    - Stake in story: Main motivations and what they have to gain/lose
    - Change/Development: Changes in this character's persona, and the growth they undergo.
    - Relationships: Core relationships with other characters, including family, friends, enemies, and lovers.
    
    Your output should adhere to this format:
    {{
        "Character": {character},
        "Basic Role": "{{Character information here}}",
        "Physical Descriptions": "{{Character information here}}",
        "Personality Descriptions": "{{Character information here}}",
        "Stake in the Story": "{{Character information here (if applicable)}}",
        "Change/Development": "{{Character information here (if applicable)}}",
        "Relationships": "{{Character information here (if applicable)}}"
    }}
    """

    template_message = [SystemMessagePromptTemplate(prompt=PromptTemplate(
        input_variables=['character', 'recognition_str'], template=template_str)),
        HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['passage_block'],
            template="User Query: Here are the passages to analyze: {passage_block}"))]
    
    template = ChatPromptTemplate(
        input_variables=['character', 'recognition_str', 'passage_block'],
        messages=template_message
    )
    
    template = template.partial(character=character, recognition_str=recognition_str)
    return template

def add_to_character_sheet(passages: list[str], character: str, aliases: set[str], last_sheet: dict):
    pass

