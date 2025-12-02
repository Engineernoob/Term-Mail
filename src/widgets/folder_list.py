"""Folder list widget"""

from textual.widgets import ListView, ListItem
from textual.message import Message
from textual import RenderableType
from rich.text import Text
from typing import List, Optional
from ..models.folder import Folder


class FolderItem(ListItem):
    """Individual folder item"""
    
    def __init__(self, folder: Folder):
        self.folder = folder
        super().__init__()
    
    def render(self) -> RenderableType:
        """Render folder with rich formatting"""
        text = Text()
        
        # Folder icon/name
        folder_name = self.folder.display_name
        if self.folder.name.upper() == "INBOX":
            text.append("📥 ", style="blue")
        elif self.folder.name.upper() == "SENT":
            text.append("📤 ", style="green")
        elif self.folder.name.upper() == "DRAFTS":
            text.append("📝 ", style="yellow")
        elif self.folder.name.upper() == "TRASH":
            text.append("🗑 ", style="red")
        else:
            text.append("📁 ", style="dim")
        
        text.append(folder_name, style="")
        
        # Unread count badge
        if self.folder.unread_count > 0:
            text.append(f" ({self.folder.unread_count})", style="bold bright_blue")
        
        return text


class FolderList(ListView):
    """Sidebar folder navigation widget"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.folders: List[Folder] = []
    
    class FolderSelected(Message):
        """Message sent when a folder is selected"""
        def __init__(self, folder: Folder):
            self.folder = folder
            super().__init__()
    
    def load_folders(self, folders: List[Folder]):
        """Load folders into the list"""
        self.folders = folders
        self.clear()
        
        for folder in folders:
            item = FolderItem(folder)
            self.append(item)
        
        # Select INBOX by default
        for i, folder in enumerate(folders):
            if folder.name.upper() == "INBOX":
                self.index = i
                break
    
    def get_selected_folder(self) -> Optional[Folder]:
        """Get the currently selected folder"""
        if self.index is None:
            return None
        
        if 0 <= self.index < len(self.folders):
            return self.folders[self.index]
        return None
    
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle folder selection"""
        folder = self.get_selected_folder()
        if folder:
            self.post_message(self.FolderSelected(folder))

