"""Create local email address screen"""

from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Header, Footer, Input, Button, Label, Select
from textual import work
from ..utils.local_email_manager import LocalEmailManager
from ..utils.config import ConfigManager


class CreateLocalEmailScreen(Screen):
    """Screen for creating local email addresses"""
    
    BINDINGS = [
        ("ctrl+s", "create", "Create"),
        ("escape", "cancel", "Cancel"),
    ]
    
    def __init__(self, config_manager: ConfigManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config_manager = config_manager
        self.local_email_manager = LocalEmailManager()
    
    def compose(self) -> ComposeResult:
        """Compose the screen layout"""
        yield Header()
        
        with Vertical(id="create-email-container"):
            yield Label("Create Local Email Address", classes="screen-title")
            
            yield Label("Local Part (before @):", classes="field-label")
            yield Input(id="local-part-input", placeholder="username")
            
            yield Label("Domain:", classes="field-label")
            yield Input(id="domain-input", value="local", placeholder="local")
            
            yield Label("", id="email-preview")
            
            yield Label("SMTP Configuration (Optional - for sending to external addresses):", classes="field-label")
            yield Label("Leave blank to use only for local emails", classes="hint")
            
            yield Label("SMTP Server:", classes="field-label")
            yield Input(id="smtp-server-input", placeholder="smtp.gmail.com")
            
            yield Label("SMTP Port:", classes="field-label")
            yield Input(id="smtp-port-input", value="587", placeholder="587")
            
            yield Label("SMTP Username:", classes="field-label")
            yield Input(id="smtp-username-input", placeholder="your-email@gmail.com")
            
            yield Label("SMTP Password:", classes="field-label")
            yield Input(id="smtp-password-input", password=True, placeholder="Your SMTP password")
            
            with Horizontal(id="button-bar"):
                yield Button("Create", id="create-button", variant="primary")
                yield Button("Cancel", id="cancel-button")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Called when screen is mounted"""
        local_part_input = self.query_one("#local-part-input", Input)
        local_part_input.focus()
        self.update_preview()
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Update email preview when input changes"""
        self.update_preview()
    
    def update_preview(self):
        """Update the email preview"""
        local_part = self.query_one("#local-part-input", Input).value.strip()
        domain = self.query_one("#domain-input", Input).value.strip() or "local"
        
        if local_part:
            preview = f"{local_part}@{domain}"
            preview_label = self.query_one("#email-preview", Label)
            preview_label.update(f"Email address: {preview}")
        else:
            preview_label = self.query_one("#email-preview", Label)
            preview_label.update("")
    
    @work(exclusive=True)
    async def action_create(self):
        """Create the email address"""
        local_part = self.query_one("#local-part-input", Input).value.strip()
        domain = self.query_one("#domain-input", Input).value.strip() or "local"
        
        if not local_part:
            self.app.bell()
            return
        
        # Validate local part (basic validation)
        if not local_part.replace("_", "").replace("-", "").replace(".", "").isalnum():
            self.app.bell()
            return
        
        try:
            # Create email address
            account = self.local_email_manager.create_email_address(local_part, domain)
            
            # Add SMTP configuration if provided
            smtp_server = self.query_one("#smtp-server-input", Input).value.strip()
            smtp_port = self.query_one("#smtp-port-input", Input).value.strip()
            smtp_username = self.query_one("#smtp-username-input", Input).value.strip()
            smtp_password = self.query_one("#smtp-password-input", Input).value.strip()
            
            if smtp_server and smtp_username and smtp_password:
                account["smtp_server"] = smtp_server
                account["smtp_port"] = int(smtp_port) if smtp_port else 587
                account["smtp_username"] = smtp_username
                account["smtp_password"] = smtp_password
                account["use_tls"] = True
            
            # Add to accounts
            account_id = self.config_manager.add_account(account)
            
            # Refresh provider in app
            if hasattr(self.app, 'initialize_provider'):
                self.app.initialize_provider()
            if hasattr(self.app, 'connect_provider') and self.app.provider:
                success = await self.app.connect_provider()
                if success:
                    self.app.pop_screen()
                    self.app.push_screen("inbox")
                else:
                    self.app.bell()
            else:
                self.app.pop_screen()
        except ValueError as e:
            # Show error
            preview_label = self.query_one("#email-preview", Label)
            preview_label.update(f"Error: {str(e)}", classes="error")
            self.app.bell()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "create-button":
            self.action_create()
        elif event.button.id == "cancel-button":
            self.action_cancel()
    
    def action_cancel(self):
        """Cancel creation"""
        self.app.pop_screen()

