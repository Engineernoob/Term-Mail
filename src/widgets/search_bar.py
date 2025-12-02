"""Search bar widget"""

from textual.widgets import Input
from textual.message import Message
from typing import Optional


class SearchBar(Input):
    """Search input widget"""
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("placeholder", "Search emails...")
        super().__init__(*args, **kwargs)
    
    class SearchSubmitted(Message):
        """Message sent when search is submitted"""
        def __init__(self, query: str):
            self.query = query
            super().__init__()
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle search submission"""
        query = self.value.strip()
        if query:
            self.post_message(self.SearchSubmitted(query))
    
    def clear_search(self):
        """Clear the search input"""
        self.value = ""

