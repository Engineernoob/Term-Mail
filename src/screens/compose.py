"""Compose email screen"""

from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Header, Footer, Input, TextArea, Button, Label
from textual import work
from typing import Optional, Dict, Any
from ..models.email import Email
from ..providers.base import EmailProvider


class ComposeScreen(Screen):
    """Screen for composing emails"""
    
    BINDINGS = [
        ("ctrl+s", "send", "Send"),
        ("escape", "cancel", "Cancel"),
    ]
    
    def __init__(
        self,
        provider: EmailProvider,
        reply_to: Optional[Email] = None,
        forward: Optional[Email] = None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.provider = provider
        self.reply_to = reply_to
        self.forward = forward
        self.mode = "compose"
        if reply_to:
            self.mode = "reply"
        elif forward:
            self.mode = "forward"
    
    def compose(self) -> ComposeResult:
        """Compose the screen layout"""
        yield Header(show_clock=True)
        
        with Vertical(id="compose-container"):
            mode_icon = "✉️" if self.mode == "compose" else "↩️" if self.mode == "reply" else "↪️"
            yield Label(f"{mode_icon} {self.mode.title()} Email", classes="screen-title")
            
            yield Label("To:", classes="field-label")
            to_value = ""
            if self.reply_to:
                to_value = self.reply_to.from_email
            elif self.forward:
                to_value = ""
            yield Input(id="to-input", value=to_value)
            
            yield Label("CC:", classes="field-label")
            yield Input(id="cc-input")
            
            yield Label("Subject:", classes="field-label")
            subject_value = ""
            if self.reply_to:
                subject_value = f"Re: {self.reply_to.subject}"
            elif self.forward:
                subject_value = f"Fwd: {self.forward.subject}"
            yield Input(id="subject-input", value=subject_value)
            
            yield Label("Body:", classes="field-label")
            body_value = ""
            if self.reply_to:
                body_value = f"\n\n--- Original Message ---\n"
                body_value += f"From: {self.reply_to.from_address}\n"
                body_value += f"Date: {self.reply_to.date}\n"
                body_value += f"\n{self.reply_to.body_text}\n"
            elif self.forward:
                body_value = f"\n\n--- Forwarded Message ---\n"
                body_value += f"From: {self.forward.from_address}\n"
                body_value += f"Date: {self.forward.date}\n"
                body_value += f"Subject: {self.forward.subject}\n"
                body_value += f"\n{self.forward.body_text}\n"
            yield TextArea(id="body-input", value=body_value)
            
            with Horizontal(id="button-bar"):
                yield Button("Send", id="send-button", variant="primary")
                yield Button("Cancel", id="cancel-button")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Called when screen is mounted"""
        to_input = self.query_one("#to-input", Input)
        to_input.focus()
    
    @work(exclusive=True)
    async def action_send(self):
        """Send the email"""
        to_input = self.query_one("#to-input", Input)
        cc_input = self.query_one("#cc-input", Input)
        subject_input = self.query_one("#subject-input", Input)
        body_input = self.query_one("#body-input", TextArea)
        
        to_addresses = [addr.strip() for addr in to_input.value.split(",") if addr.strip()]
        cc_addresses = [addr.strip() for addr in cc_input.value.split(",") if addr.strip()] if cc_input.value else None
        
        if not to_addresses:
            self.app.bell()
            return
        
        subject = subject_input.value
        body = body_input.text
        
        reply_to_id = None
        if self.reply_to:
            reply_to_id = self.reply_to.id
        
        success = await self.provider.send_email(
            to_addresses=to_addresses,
            subject=subject,
            body=body,
            cc_addresses=cc_addresses,
            reply_to_id=reply_to_id
        )
        
        if success:
            self.app.pop_screen()
        else:
            self.app.bell()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "send-button":
            self.action_send()
        elif event.button.id == "cancel-button":
            self.action_cancel()
    
    def action_cancel(self):
        """Cancel composition"""
        self.app.pop_screen()

