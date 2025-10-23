from abc import ABC, abstractmethod

"""
Text Data:
A text has:
    string content
    text type (e.g., paragraph, heading, list item)
    attributes (e.g., bold, italic, underline)
    ai tags (e.g., summarized, key points, questions)
    
    
Ideation:
    We have a tree structure of nodes.
    
    It will look something like this:
    Document
    ├── ParagraphNode
    │    ├── TextNode("Harry looked at Ron and said, ")
    │    ├── DialogueNode(character="Ron")
    │    │     └── TextNode("Blimey, mate!")
    │    └── TextNode(" Ron laughed.", attributes={"italic"})
    └── ParagraphNode
        └── TextNode("It was a normal day at Hogwarts.")
        
Heres my idea for Node inheritance:
A Node is a text node or a feature node

A text node is either:
AIStamp
Plaintext

A feature node is either:
AIautofil
Comment (maybe?)
            

NOTE: The implemenation below is mainly expiremental

"""

ATTRIBUTES = {"bold", "italic", "underline"}

TEXTYPES = set()

class Node(ABC):
    """
    A node from our document tree.
    """
    # This may be scrapped
    @abstractmethod 
    def is_ai_feature(self) -> bool:
        pass
    
    @abstractmethod
    def is_ai_tagged(self) -> bool:
        pass
    
    @abstractmethod
    def to_dict(self) -> dict:
        pass
    
    @abstractmethod
    def get_texttype(self) -> str:
        pass
    
    @abstractmethod
    def get_plaintext(self) -> str:
        pass
    
    @abstractmethod
    def get_attributes(self) -> dict:
        pass
    
    @abstractmethod
    def has_ai_tags(self) -> bool:
        return self.ai_tags() != {}
    
    @abstractmethod
    def add_child(self, child_node: 'Node') -> None:
        pass
    
    @abstractmethod
    def get_children(self) -> list['Node']:
        pass
    
    @abstractmethod
    def remove_child(self, child_node: 'Node') -> None:
        pass
    
    

class TextNode(Node):
    """
    A text node in the document tree.
    The most basic node
    """
    
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

    def add_child(self, child_node: Node):
        self.children.append(child_node)

    def get_children(self):
        raise NotImplementedError

    def remove_child(self, child_node):
        raise NotImplementedError

    
class StampNode(Node):
    """
    A node representing an AI stamp.
    """

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

    def add_child(self, child_node):
        raise NotImplementedError

    def get_children(self):
        raise NotImplementedError

    def remove_child(self, child_node):
        raise NotImplementedError




    
class DocumentNode(Node):
    """
    A document consisting of nodes in a tree structure.
    
    """
    def __init__(self, root: Node):
        self.root = root
        
    