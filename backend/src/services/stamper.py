import ABC, abstract_method
from backend.src.models.scrap.nodes import Node, DocumentNode, TextNode, StampNode
from langchain import LLMChain


class Stamper(ABC):
    """
    Modifies Nodes by adding AI stamps.
    """
    
    @abstract_method
    def stamp_node(self, node: Node) -> StampNode:
        assert isinstance(node, Node)
        pass
    
    @abstract_method
    def get_llm_chain(self) -> LLMChain:
        pass