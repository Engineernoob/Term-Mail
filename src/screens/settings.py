"""Settings screen"""

from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Header, Footer, Input, Button, Label, Select, RadioSet, RadioButton
from textual import work
from typing import Optional
from ..providers.base import EmailProvider
from ..providers.nylas_provider import NylasProvider
from ..providers.imap_provider import IMAPProvider
from ..utils.config import ConfigManager


class SettingsScreen(Screen):
    """Settings and account management screen"""
    
    BINDINGS = [
        ("b", "back", "Back"),
        ("q", "quit", "Quit"),
    ]
    
    def __init__(self, config_manager: ConfigManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config_manager = config_manager
        self.current_provider_type = "imap"
    
    def compose(self) -> ComposeResult:
        """Compose the screen layout"""
        yield Header()
        
        with Vertical(id="settings-container"):
            yield Label("Account Settings", classes="screen-title")
            
            # Show existing accounts
            accounts = self.config_manager.get_accounts()
            if accounts:
                yield Label("Existing Accounts:", classes="field-label")
                for account in accounts:
                    account_name = account.get("name", account.get("email", account.get("email_address", "Unknown")))
                    provider_type = account.get("provider", "unknown")
                    account_id = account.get("id", "")
                    
                    account_info = f"{account_name} ({provider_type})"
                    if provider_type == "local" and not account.get("smtp_server"):
                        account_info += " [Local only - no SMTP configured]"
                    
                    yield Label(account_info, classes="account-info")
                    
                    if provider_type == "local":
                        yield Button(
                            f"Configure SMTP for {account_name}",
                            id=f"configure-smtp-{account_id}",
                            classes="account-button"
                        )
            
            yield Label("", classes="separator")
            yield Label("Add New Account", classes="section-title")
            
            yield Label("Provider Type:", classes="field-label")
            yield RadioSet(
                RadioButton("IMAP/SMTP", id="provider-imap"),
                RadioButton("Nylas", id="provider-nylas"),
                RadioButton("Local Email", id="provider-local"),
                id="provider-select"
            )
            
            # IMAP/SMTP fields
            with Container(id="imap-fields"):
                yield Label("Email:", classes="field-label")
                yield Input(id="email-input", placeholder="your@email.com")
                
                yield Label("Password:", classes="field-label")
                yield Input(id="password-input", password=True)
                
                yield Label("IMAP Server:", classes="field-label")
                yield Input(id="imap-server-input", placeholder="imap.gmail.com")
                
                yield Label("IMAP Port:", classes="field-label")
                yield Input(id="imap-port-input", value="993")
                
                yield Label("SMTP Server:", classes="field-label")
                yield Input(id="smtp-server-input", placeholder="smtp.gmail.com")
                
                yield Label("SMTP Port:", classes="field-label")
                yield Input(id="smtp-port-input", value="587")
            
            # Nylas fields
            with Container(id="nylas-fields", classes="hidden"):
                yield Label("API Key:", classes="field-label")
                yield Input(id="nylas-api-key-input", placeholder="Your Nylas API key")
                
                yield Label("Access Token:", classes="field-label")
                yield Input(id="nylas-access-token-input", placeholder="Your access token")
                
                yield Label("Grant ID:", classes="field-label")
                yield Input(id="nylas-grant-id-input", placeholder="Your grant ID")
            
            with Horizontal(id="button-bar"):
                yield Button("Add Account", id="add-account-button", variant="primary")
                yield Button("Create Local Email", id="create-local-button")
                yield Button("Back", id="back-button")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Called when screen is mounted"""
        provider_select = self.query_one("#provider-select", RadioSet)
        provider_select.pressed = "provider-imap"
    
    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        """Handle provider type change"""
        imap_fields = self.query_one("#imap-fields")
        nylas_fields = self.query_one("#nylas-fields")
        
        if event.pressed.id == "provider-imap":
            self.current_provider_type = "imap"
            imap_fields.remove_class("hidden")
            nylas_fields.add_class("hidden")
        elif event.pressed.id == "provider-nylas":
            self.current_provider_type = "nylas"
            imap_fields.add_class("hidden")
            nylas_fields.remove_class("hidden")
        elif event.pressed.id == "provider-local":
            # For local emails, open the create local email screen
            self.app.push_screen("create_local_email")
            # Reset to IMAP selection
            provider_select = self.query_one("#provider-select", RadioSet)
            provider_select.pressed = "provider-imap"
            self.current_provider_type = "imap"
    
    @work(exclusive=True)
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "add-account-button":
            await self.add_account()
        elif event.button.id == "create-local-button":
            self.app.push_screen("create_local_email")
        elif event.button.id == "back-button":
            self.action_back()
        elif event.button.id and event.button.id.startswith("configure-smtp-"):
            account_id = event.button.id.replace("configure-smtp-", "")
            self.app.push_screen("configure_smtp", account_id)
    
    async def add_account(self):
        """Add a new account"""
        if self.current_provider_type == "imap":
            email = self.query_one("#email-input", Input).value
            password = self.query_one("#password-input", Input).value
            imap_server = self.query_one("#imap-server-input", Input).value
            imap_port = int(self.query_one("#imap-port-input", Input).value or "993")
            smtp_server = self.query_one("#smtp-server-input", Input).value
            smtp_port = int(self.query_one("#smtp-port-input", Input).value or "587")
            
            if not all([email, password, imap_server, smtp_server]):
                self.app.bell()
                return
            
            account = {
                "provider": "imap",
                "email": email,
                "password": password,
                "imap_server": imap_server,
                "imap_port": imap_port,
                "smtp_server": smtp_server,
                "smtp_port": smtp_port,
                "use_tls": True,
            }
        else:
            api_key = self.query_one("#nylas-api-key-input", Input).value
            access_token = self.query_one("#nylas-access-token-input", Input).value
            grant_id = self.query_one("#nylas-grant-id-input", Input).value
            
            if not all([api_key, access_token, grant_id]):
                self.app.bell()
                return
            
            account = {
                "provider": "nylas",
                "api_key": api_key,
                "access_token": access_token,
                "grant_id": grant_id,
            }
        
        account_id = self.config_manager.add_account(account)
        # Refresh provider in app
        if hasattr(self.app, 'initialize_provider'):
            self.app.initialize_provider()
        if hasattr(self.app, 'connect_provider') and self.app.provider:
            success = await self.app.connect_provider()
            if success:
                # Switch to inbox if we just added the first account
                self.app.pop_screen()
                self.app.push_screen("inbox")
            else:
                self.app.bell()
        else:
            self.app.pop_screen()
    
    def action_back(self):
        """Go back to inbox"""
        self.app.pop_screen()
    
    def action_quit(self):
        """Quit application"""
        self.app.exit()

