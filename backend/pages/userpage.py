"""
Represents the actual novel of the user is writing.
Consists of one to many chapters.
"""
from backend.pages.assistantpage import Macro
class TextBlock:
    def __init__(self, block: list[str | Macro]):
        self.block = block

class UserPage:
    def __init__(self):
        chapters: dict[str, TextBlock] = {}
        
    def modify_chapter(self, chapter: str, new_text: TextBlock):
        self.chapters[chapter] = new_text

