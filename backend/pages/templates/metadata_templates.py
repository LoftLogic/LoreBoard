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
    
    previous = ""
    if last_summaries:
        previous == f"The given chapter is not the start of the story chronologically. First read the previous summarization for context, then, go through the given chapter and record notes. Here are the summaries of all previous plot events:"
        for summ in last_summaries:
            previous += "\n" + summ
            
    template_str = """
    # Prompt
    Objective: Your to act as a creative writing assistant focused on chapter analysis. 
    {previous_summaries}
    Your given a chapter to read and analyze, and record notes as you do so. These notes are kept as reference for the writer, as such they should be informative and not just taken verbatim from the passage text.
    
    You are to record the following as you read the chapter.
    - Plot Summary: A summary of the events that take place. This section is very important as its used by other LLMs for context as they summarize future chapters
    - Characters: A summary of charaterizations that occur in the chapter. Organize notes by character
    - Tone: The general tone of the chapter, or how it changes as the story progresses
    - World: Any worldbuilding accomplished, if applicable
    - Themes: The explored themes and concepts within the chapter, if applicable
    - Viewer Enjoyment: What aspects of this chapter appeal to audience members, if applicable
    
    Your output should adhere to this format:
    {{
        "Plot Summary": {{Chapter information here, this will be used by future LLMs as context}},
        "Characters": {{Chapter information here}},
        "Tone": "{{Chapter information here}}",
        "World": "{{Chapter information here}}",
        "Themes": "{{Chapter information here}}",
        "Viewer Enjoyment: "{{Chapter information here}}",
    }}
    """
    
    template_message = [SystemMessagePromptTemplate(prompt=PromptTemplate(
        input_variables=['passage', 'previous_summaries'], template=template_str)),
        HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['passage'],
            template="User Query: Here is the passage to analyze: {passage}"))]
    
    template = ChatPromptTemplate(
        input_variables=['passage', 'previous_summaries'],
        messages=template_message
    )
    
    template = template.partial(passage=passage, previous_summaries=previous)
    return template