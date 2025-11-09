from abc import ABC, abstractmethod

from nanoid import generate

"""
Text Data:
A text has:
    string content
    text type (e.g., basic, chapter, etc)
    attributes (e.g., bold, italic, underline)
    ai tags (e.g., summarized, key points, questions)
    
    
Ideation:
    We have a tree structure of nodes.
    
    It will look something like this:
    ChapterNode
    ├── ParagraphNode
    │    ├── TextNode("Harry looked at Ron and said, ")
    │    ├── InteractionNode(characters="Ron", "Harry") # This is an AI Stamp
    │    │     └── TextNode("Blimey, mate!")
    │    └── TextNode(" Ron laughed.", attributes={"italic"})
    └── ParagraphNode
        └── TextNode("It was a normal day at Hogwarts.")
        




NOTE: The implemenation below is mainly expiremental
"""

ATTRIBUTES = {"bold", "italic", "underline"}

TEXTTYPES = {"Title", "Chapter", "Subheading", "Basic"}

class Node(ABC):
    """
    A node from our document tree.
    """
    @abstractmethod
    def to_dict(self) -> dict:
        """
        Transforms this node into a dictionary
        DOES NOT RECURSE
        """
        pass
    
    @abstractmethod
    def to_dict_recurse(self):
        """
        Transforms this node into a dictionary
        CALLS THIS ON ALL NESTED NODES
        """
        pass
    
    
    @abstractmethod
    def get_plaintext(self) -> str:
        pass
    
    
    @abstractmethod
    def add_child(self, child: 'Node') -> None:
        pass
    
    def add_children(self, children: list['Node']) -> None:
        for child in children:
            self.add_child(child)
    
    
    @abstractmethod
    def get_children(self) -> list['Node']:
        pass
    
    @abstractmethod
    def remove_child(self, child: 'Node') -> None:
        pass
    
    @abstractmethod
    def get_rank(self) -> int:
        pass
    
    def has_child(self, child: 'Node') -> bool:
        return child in self.get_children
    
class DocumentNode(Node):
    """
    A document consisting of nodes in a tree structure.
    The root node in a document.
    
    Invariants:

    """
    rank = 1
    
    def __init__(self, title: str,  font_size = 12):
        self.title = title
        self.font_size = font_size
        self.children: list[ChapterNode] = []

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "font_size" : self.font_size,
            "children": self.children
        }


    def to_dict_recurse(self):
        return {
            "title": self.title,
            "font_size" : self.font_size,
            "children": list(map(lambda node: node.to_dict_recurse(), self.children))
        }

    def get_plaintext(self):
        raise NotImplementedError

    def add_child(self, child):
        assert self.get_rank() <= child.get_rank()
        
        self.children.append(child)

    def get_children(self):
        return self.children

    def remove_child(self, child):
        self.children.pop(child)

    def get_rank(self) -> int:
        return DocumentNode.rank
        
class ChapterNode(Node):
    """
    A chapter in the document.
    """
    rank = 2
    
    def __init__(self, title: str, subheading: str = ""):
        self.title = title
        self.subheading = subheading
        self.children: list['ParagraphNode'] = []

    def to_dict(self):
        return {
            "title": self.title,
            "subheading": self.subheading,
            "children": self.children
        }
        
    def to_dict_recurse(self):
        raise NotImplementedError

    def get_plaintext(self):
        raise NotImplementedError

    def add_child(self, child):
        self.get_rank() <= child.get_rank()
        raise NotImplementedError

    def get_children(self):
        raise NotImplementedError

    def remove_child(self, child):
        raise NotImplementedError

    def get_rank(self):
        return self.rank
    
    

class ParagraphNode(Node):
    """
    A node representing the beginning of a paragraph
    """
    rank = 3

class StampNode(Node):
    """
    A node representing an AI stamp.
    """
    rank = 4
    
    def is_ai_feature(self):
        raise NotImplementedError

    def is_ai_tagged(self):
        raise NotImplementedError

    def to_dict(self):
        raise NotImplementedError

    def get_texttype(self):
        raise NotImplementedError

    def get_plaintext(self):
        raise NotImplementedError

    def get_attributes(self):
        raise NotImplementedError

    def has_ai_tags(self):
        raise NotImplementedError

    def add_child(self, child):
        self.get_rank() <= child.get_rank()
        raise NotImplementedError

    def get_children(self):
        raise NotImplementedError

    def remove_child(self, child):
        raise NotImplementedError

class TextNode(Node):
    """
    A text node in the document tree.
    The most basic node
    """
    rank = 5
    
    def __init__(self, plaintext: str, texttype: str, attributes: set = None, ai_tags: dict = None):
        assert all(attr in ATTRIBUTES for attr in (attributes or set())), "Invalid attributes"
        
        self.plaintext = plaintext
        self.texttype = texttype
        self.attributes = attributes if attributes is not None else set()
        self.ai_tags = ai_tags if ai_tags is not None else {}
        self.children = []
        self.parent = None

    def is_ai_feature(self) -> bool:
        return False

    def is_ai_tagged(self) -> bool:
        return self.ai_tags != {}

    def to_dict(self):
        return {
            "plaintext": self.plaintext,
            "texttype": self.texttype,
            "attributes": list(self.attributes),
            "ai_tags": self.ai_tags
        }

    def get_texttype(self) -> str:
        return self.texttype

    def get_plaintext(self) -> str:
        return self.plaintext

    def get_attributes(self):
        return self.attributes

    def ai_tags(self):
        return self.ai_tags

    def has_ai_tags(self):
        return self.ai_tags != {}

    def add_child(self, child: Node):
        self.get_rank() <= child.get_rank()
        self.children.append(child)

    def get_children(self):
        raise NotImplementedError

    def remove_child(self, child):
        raise NotImplementedError