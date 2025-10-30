class Entity:
    """
    Event triggered when the user registers a new entity
    """
    def __init__(self, name, aliases = set()):
        self.name: str
        self.aliases: set[str] = aliases
        
    def name(self) -> str:
        return self.name
        
    def set_aliases(self, new_aliases: set[str]):
        self.aliases = new_aliases
        
    def add_alias(self, alias):
        self.aliases.add(alias)
        
    def remove_alias(self, alias):
        self.aliases.remove(alias)