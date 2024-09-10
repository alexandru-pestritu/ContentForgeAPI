class GutenbergBlock:
    def __init__(self, block_type: str, attrs: dict = None, inner_content: str = ""):
        """
        :param block_type: Block type (ex: 'heading', 'paragraph', 'spacer', etc.)
        :param attrs: Specific attributes of the block as a dictionary (optional).
        :param inner_content: Inner content of the block (optional).
        """
        self.block_type = block_type
        self.attrs = attrs if attrs else {}
        self.inner_content = inner_content

    def attrs_to_string(self) -> str:
        """Convert attributes dictionary to a string in JSON-like format for Gutenberg"""
        if not self.attrs:
            return ""
        attrs_str = str(self.attrs).replace("'", '"').replace("True", "true").replace("False", "false")
        return f" {attrs_str}"

    def render(self) -> str:
        """Render the block in Gutenberg format"""
        attrs_str = self.attrs_to_string()
        return f"<!-- wp:{self.block_type}{attrs_str} -->{self.inner_content}<!-- /wp:{self.block_type} -->"
    
    def escape_to_unicode(self, text: str) -> str:
        """Transform special characters into Unicode escape sequences."""
        return (text.replace("<", "\\u003c")
                    .replace(">", "\\u003e")
                    .replace('"', "\\u0022")
                    .replace("&", "\\u0026"))
