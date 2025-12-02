"""Message list widget"""

from textual.widgets import ListView, ListItem
from textual.message import Message
from textual.containers import Horizontal, Vertical
from textual.widgets import Label
from textual import RenderableType
from rich.text import Text
from typing import List, Optional
from datetime import datetime
from ..models.email import Email


class MessageItem(ListItem):
    """Individual message item in the list"""
    
    def __init__(self, email: Email):
        self.email = email
        super().__init__()
        self.add_class("message-item-unread" if not email.is_read else "message-item-read")
    
    def render(self) -> RenderableType:
        """Render the message item with rich formatting"""
        # Create rich text for better formatting
        text = Text()
        
        # Unread indicator
        if not self.email.is_read:
            text.append("● ", style="bold bright_blue")
        else:
            text.append("  ", style="")
        
        # Star indicator
        if self.email.is_starred:
            text.append("★ ", style="bold yellow")
        else:
            text.append("  ", style="")
        
        # Attachment indicator
        if self.email.attachments:
            text.append("📎 ", style="cyan")
        else:
            text.append("   ", style="")
        
        # From name
        from_name = self.email.from_name[:28] + "..." if len(self.email.from_name) > 28 else self.email.from_name
        if not self.email.is_read:
            text.append(f"{from_name:<32}", style="bold")
        else:
            text.append(f"{from_name:<32}", style="dim")
        
        # Subject
        subject = self.email.subject[:48] + "..." if len(self.email.subject) > 48 else self.email.subject
        if not self.email.is_read:
            text.append(f"{subject:<52}", style="bold")
        else:
            text.append(f"{subject:<52}", style="dim")
        
        # Date
        date_str = self._format_date(self.email.date)
        text.append(date_str, style="dim")
        
        return text
    
    def _format_date(self, date: datetime) -> str:
        """Format date for display"""
        now = datetime.now()
        diff = now - date
        
        if diff.days == 0:
            return date.strftime("%H:%M")
        elif diff.days < 7:
            return date.strftime("%a")
        elif diff.days < 365:
            return date.strftime("%b %d")
        else:
            return date.strftime("%Y")


class MessageList(ListView):
    """Scrollable list of email messages"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.messages: List[Email] = []
    
    class MessageSelected(Message):
        """Message sent when a message is selected"""
        def __init__(self, email: Email):
            self.email = email
            super().__init__()
    
    def load_messages(self, messages: List[Email]):
        """Load messages into the list"""
        self.messages = messages
        self.clear()
        
        for email in messages:
            item = MessageItem(email)
            self.append(item)
        
        if messages:
            self.index = 0
    
    def get_selected_email(self) -> Optional[Email]:
        """Get the currently selected email"""
        if self.index is None:
            return None
        
        if 0 <= self.index < len(self.messages):
            return self.messages[self.index]
        return None
    
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle message selection"""
        email = self.get_selected_email()
        if email:
            self.post_message(self.MessageSelected(email))
    
    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        """Handle when item is highlighted (for preview updates)"""
        email = self.get_selected_email()
        if email:
            self.post_message(self.MessageSelected(email))
    
    def update_message_status(self, email_id: str, is_read: bool):
        """Update the read status of a message"""
        for i, email in enumerate(self.messages):
            if email.id == email_id:
                email.is_read = is_read
                # Update the list item
                if i < len(self.children):
                    item = MessageItem(email)
                    self.children[i] = item
                    # Update classes
                    if is_read:
                        item.remove_class("message-item-unread")
                        item.add_class("message-item-read")
                    else:
                        item.remove_class("message-item-read")
                        item.add_class("message-item-unread")
                break

