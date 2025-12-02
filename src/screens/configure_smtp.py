"""Configure SMTP for local email address screen"""

from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Header, Footer, Input, Button, Label
from textual import work
from ..utils.config import ConfigManager


class ConfigureSMTPScreen(Screen):
    """Screen for configuring SMTP for a local email address"""
    
    BINDINGS = [
        ("ctrl+s", "save", "Save"),
        ("escape", "cancel", "Cancel"),
    ]
    
    def __init__(self, config_manager: ConfigManager, account_id: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config_manager = config_manager
        self.account_id = account_id
        self.account = config_manager.get_account(account_id)
    
    def compose(self) -> ComposeResult:
        """Compose the screen layout"""
        yield Header()
        
        email_address = self.account.get("email_address", "") if self.account else ""
        
        with Vertical(id="configure-smtp-container"):
            yield Label(f"Configure SMTP for {email_address}", classes="screen-title")
            
            yield Label("SMTP Configuration (for sending to external addresses):", classes="field-label")
            yield Label("Leave blank to use only for local emails", classes="hint")
            
            yield Label("SMTP Server:", classes="field-label")
            yield Input(
                id="smtp-server-input",
                value=self.account.get("smtp_server", "") if self.account else "",
                placeholder="smtp.gmail.com"
            )
            
            yield Label("SMTP Port:", classes="field-label")
            yield Input(
                id="smtp-port-input",
                value=str(self.account.get("smtp_port", 587)) if self.account else "587",
                placeholder="587"
            )
            
            yield Label("SMTP Username:", classes="field-label")
            yield Input(
                id="smtp-username-input",
                value=self.account.get("smtp_username", "") if self.account else "",
                placeholder="your-email@gmail.com"
            )
            
            yield Label("SMTP Password:", classes="field-label")
            yield Input(
                id="smtp-password-input",
                password=True,
                value=self.account.get("smtp_password", "") if self.account else "",
                placeholder="Your SMTP password"
            )
            
            with Horizontal(id="button-bar"):
                yield Button("Save", id="save-button", variant="primary")
                yield Button("Clear SMTP", id="clear-button")
                yield Button("Cancel", id="cancel-button")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Called when screen is mounted"""
        smtp_server_input = self.query_one("#smtp-server-input", Input)
        smtp_server_input.focus()
    
    @work(exclusive=True)
    async def action_save(self):
        """Save SMTP configuration"""
        smtp_server = self.query_one("#smtp-server-input", Input).value.strip()
        smtp_port = self.query_one("#smtp-port-input", Input).value.strip()
        smtp_username = self.query_one("#smtp-username-input", Input).value.strip()
        smtp_password = self.query_one("#smtp-password-input", Input).value.strip()
        
        updates = {}
        
        if smtp_server and smtp_username and smtp_password:
            updates["smtp_server"] = smtp_server
            updates["smtp_port"] = int(smtp_port) if smtp_port else 587
            updates["smtp_username"] = smtp_username
            updates["smtp_password"] = smtp_password
            updates["use_tls"] = True
        else:
            # Clear SMTP config
            updates["smtp_server"] = None
            updates["smtp_port"] = None
            updates["smtp_username"] = None
            updates["smtp_password"] = None
        
        self.config_manager.update_account(self.account_id, updates)
        
        # Refresh provider in app
        if hasattr(self.app, 'initialize_provider'):
            self.app.initialize_provider()
        
        self.app.pop_screen()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "save-button":
            self.action_save()
        elif event.button.id == "clear-button":
            # Clear all SMTP fields
            self.query_one("#smtp-server-input", Input).value = ""
            self.query_one("#smtp-port-input", Input).value = "587"
            self.query_one("#smtp-username-input", Input).value = ""
            self.query_one("#smtp-password-input", Input).value = ""
        elif event.button.id == "cancel-button":
            self.action_cancel()
    
    def action_cancel(self):
        """Cancel configuration"""
        self.app.pop_screen()

