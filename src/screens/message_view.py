"""Message view screen"""

from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Header, Footer, Label, Button, Static
from textual import work
from ..models.email import Email
from ..providers.base import EmailProvider
from ..utils.html_parser import html_to_text


class MessageViewScreen(Screen):
    """Screen for viewing an individual email message"""
    
    BINDINGS = [
        ("r", "reply", "Reply"),
        ("f", "forward", "Forward"),
        ("d", "delete", "Delete"),
        ("u", "mark_unread", "Mark Unread"),
        ("b", "back", "Back"),
        ("q", "quit", "Quit"),
    ]
    
    def __init__(self, email: Email, provider: EmailProvider, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.email = email
        self.provider = provider
    
    def compose(self) -> ComposeResult:
        """Compose the screen layout"""
        yield Header(show_clock=True)
        
        with Vertical(id="message-container"):
            # Header information
            with Container(id="message-header"):
                # Status indicators
                status_icons = ""
                if not self.email.is_read:
                    status_icons += "● "
                if self.email.is_starred:
                    status_icons += "★ "
                if self.email.attachments:
                    status_icons += f"📎 ({len(self.email.attachments)})"
                
                if status_icons:
                    yield Label(status_icons, classes="header-line")
                
                yield Label(f"From: {self.email.from_address}", classes="header-line")
                yield Label(f"To: {', '.join(self.email.to_addresses)}", classes="header-line")
                if self.email.cc_addresses:
                    yield Label(f"CC: {', '.join(self.email.cc_addresses)}", classes="header-line")
                yield Label(f"Subject: {self.email.subject}", classes="header-line")
                yield Label(f"Date: {self.email.date.strftime('%Y-%m-%d %H:%M:%S')}", classes="header-line")
            
            # Message body
            body_text = self.email.body_text or html_to_text(self.email.body_html)
            yield Static(body_text, id="message-body")
            
            # Attachments
            if self.email.attachments:
                with Container(id="attachments"):
                    yield Label("Attachments:", classes="section-title")
                    for att in self.email.attachments:
                        size_kb = att.size / 1024
                        yield Label(f"  • {att.filename} ({size_kb:.1f} KB)", classes="attachment")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Called when screen is mounted"""
        # Mark as read if unread
        if not self.email.is_read:
            self.mark_as_read()
    
    @work(exclusive=True)
    async def mark_as_read(self):
        """Mark email as read"""
        await self.provider.mark_read(self.email.id, read=True)
        self.email.is_read = True
    
    def action_reply(self):
        """Reply to email"""
        self.app.push_screen("compose", {"reply_to": self.email})
    
    def action_forward(self):
        """Forward email"""
        self.app.push_screen("compose", {"forward": self.email})
    
    @work(exclusive=True)
    async def action_delete(self):
        """Delete email"""
        success = await self.provider.delete_email(self.email.id)
        if success:
            self.app.pop_screen()
    
    @work(exclusive=True)
    async def action_mark_unread(self):
        """Mark email as unread"""
        await self.provider.mark_read(self.email.id, read=False)
        self.email.is_read = False
    
    def action_back(self):
        """Go back to inbox"""
        self.app.pop_screen()
    
    def action_quit(self):
        """Quit application"""
        self.app.exit()

