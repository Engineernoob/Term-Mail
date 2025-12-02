"""Status bar widget"""

from textual.widgets import Static
from textual import RenderableType
from rich.text import Text
from typing import Optional


class StatusBar(Static):
    """Status bar showing connection and app status"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connected = False
        self.status_message = ""
        self.provider_name = ""
    
    def render(self) -> RenderableType:
        """Render status bar"""
        text = Text()
        
        # Connection status
        if self.connected:
            text.append("● ", style="bold green")
            text.append("Connected", style="green")
        else:
            text.append("○ ", style="bold red")
            text.append("Disconnected", style="red")
        
        # Provider name
        if self.provider_name:
            text.append(" | ", style="dim")
            text.append(self.provider_name, style="dim")
        
        # Status message
        if self.status_message:
            text.append(" | ", style="dim")
            text.append(self.status_message, style="dim")
        
        return text
    
    def set_connected(self, connected: bool):
        """Set connection status"""
        self.connected = connected
        self.refresh()
    
    def set_provider(self, provider_name: str):
        """Set provider name"""
        self.provider_name = provider_name
        self.refresh()
    
    def set_message(self, message: str):
        """Set status message"""
        self.status_message = message
        self.refresh()
    
    def clear_message(self):
        """Clear status message"""
        self.status_message = ""
        self.refresh()

