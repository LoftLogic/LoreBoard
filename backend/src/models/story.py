from backend.src.models.scrap.nodes import DocumentNode, Node

class Story:
    """
    Represents the story
    """
    
    def __init__(self, title: str, content: DocumentNode):
        self.title = title
        content = content
        
    def get_content(self) -> DocumentNode:
        return self.content