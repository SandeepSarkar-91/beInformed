import os

class ContextParser:
    def __init__(self, filepath="context.md"):
        self.filepath = filepath

    def read_context(self):
        if not os.path.exists(self.filepath):
            return "No context.md found."
        
        with open(self.filepath, "r") as f:
            content = f.read()
            
        # Basic parsing to extract strategy and market views
        # Could be improved with markdown parsing if needed
        return content

    def get_strict_instructions(self):
        content = self.read_context()
        # Extract section between Strategy & Instructions
        if "## Strategy & Instructions" in content:
            # Simple slice for demonstration
            parts = content.split("## Strategy & Instructions")
            if len(parts) > 1:
                sub_parts = parts[1].split("##")
                return sub_parts[0].strip()
        return "No specific instructions found."
