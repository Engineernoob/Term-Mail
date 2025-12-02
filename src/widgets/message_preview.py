"""Message preview widget for split view"""

from textual.widgets import Static, Label
from textual.containers import Vertical, Container
from textual import RenderableType
from rich.text import Text
from rich.panel import Panel
from typing import Optional
from ..models.email import Email
from ..utils.html_parser import html_to_text


class MessagePreview(Static):
    """Preview pane showing selected message"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.email: Optional[Email] = None
    
    def render(self) -> RenderableType:
        """Render message preview"""
        if not self.email:
            return Panel(
                Text("Select a message to preview\n\nUse ↑/↓ to navigate\nPress Enter to open full view", style="dim", justify="center"),
                title="Preview",
                border_style="dim"
            )
        
        # Create preview content
        preview_text = Text()
        
        # Header
        preview_text.append("From: ", style="bold")
        preview_text.append(self.email.from_address, style="")
        preview_text.append("\n")
        
        preview_text.append("To: ", style="bold")
        preview_text.append(", ".join(self.email.to_addresses[:3]), style="")
        if len(self.email.to_addresses) > 3:
            preview_text.append(f" (+{len(self.email.to_addresses) - 3} more)", style="dim")
        preview_text.append("\n")
        
        if self.email.cc_addresses:
            preview_text.append("CC: ", style="bold")
            preview_text.append(", ".join(self.email.cc_addresses[:2]), style="")
            if len(self.email.cc_addresses) > 2:
                preview_text.append(f" (+{len(self.email.cc_addresses) - 2} more)", style="dim")
            preview_text.append("\n")
        
        preview_text.append("Subject: ", style="bold")
        preview_text.append(self.email.subject, style="")
        preview_text.append("\n")
        
        preview_text.append("Date: ", style="bold")
        preview_text.append(self.email.date.strftime('%Y-%m-%d %H:%M'), style="dim")
        preview_text.append("\n\n")
        
        # Status indicators
        if not self.email.is_read:
            preview_text.append("● ", style="bold bright_blue")
        if self.email.is_starred:
            preview_text.append("★ ", style="bold yellow")
        if self.email.attachments:
            preview_text.append(f"📎 {len(self.email.attachments)} attachment(s)", style="cyan")
            preview_text.append("\n\n")
        
        # Body preview (first 800 chars, wrapped)
        body_text = self.email.body_text or html_to_text(self.email.body_html)
        if body_text:
            preview_text.append("\n", style="")
            preview_text.append("─" * 40, style="dim")
            preview_text.append("\n\n", style="")
            
            # Show more text in preview, but wrap it nicely
            preview_body = body_text[:800].strip()
            if len(body_text) > 800:
                preview_body += "\n\n... (message continues)"
            
            # Split into lines and wrap long lines
            lines = preview_body.split("\n")
            for line in lines[:20]:  # Limit to 20 lines
                if len(line) > 60:
                    # Wrap long lines
                    wrapped = [line[i:i+60] for i in range(0, len(line), 60)]
                    for wrapped_line in wrapped:
                        preview_text.append(wrapped_line, style="")
                        preview_text.append("\n", style="")
                else:
                    preview_text.append(line, style="")
                    preview_text.append("\n", style="")
            
            if len(lines) > 20:
                preview_text.append("\n... (message truncated)", style="dim italic")
        
        # Panel title with status
        title = "Preview"
        if not self.email.is_read:
            title += " ●"
        if self.email.is_starred:
            title += " ★"
        if self.email.attachments:
            title += f" 📎"
        
        return Panel(
            preview_text,
            title=title,
            border_style="blue" if not self.email.is_read else "dim"
        )
    
    def show_email(self, email: Email):
        """Show email preview"""
        self.email = email
        self.refresh()
    
    def clear(self):
        """Clear preview"""
        self.email = None
        self.refresh()

