
class Document:
    """
    
    """
    
    def __init__(self, root):
        self.root = root
        self.plaintext = ""
        self.stamp_map = []
        
    def set_root(self, root):
        self.root = root
        
        
    def update_plaintext(self):
        """
        Transforms root into a plaintext
        """
        pass
        
    def get_root(self):
        return self.root