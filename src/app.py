"""Main Textual application"""

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, Label
from typing import Optional
from .providers.base import EmailProvider
from .providers.nylas_provider import NylasProvider
from .providers.imap_provider import IMAPProvider
from .providers.local_provider import LocalProvider
from .utils.config import ConfigManager
from .screens.inbox import InboxScreen
from .screens.message_view import MessageViewScreen
from .screens.compose import ComposeScreen
from .screens.settings import SettingsScreen
from .screens.create_local_email import CreateLocalEmailScreen
from .screens.configure_smtp import ConfigureSMTPScreen
from .models.email import Email


class TermMailApp(App):
    """Main application class"""
    
    CSS = """
    /* Sidebar styling */
    .sidebar {
        width: 25;
        border-right: wide $primary;
        background: $surface;
    }
    
    .section-title {
        text-style: bold;
        margin: 1;
        color: $accent;
    }
    
    /* Main content area */
    #main-content {
        width: 1fr;
        background: $background;
    }
    
    /* Message panel (left side) */
    #message-panel {
        width: 1fr;
        min-width: 40;
    }
    
    /* Preview panel (right side) */
    .preview-panel {
        width: 40%;
        min-width: 30;
        border-left: wide $primary;
        background: $surface;
    }
    
    .preview-panel.hidden {
        display: none;
    }
    
    #message-preview {
        height: 1fr;
        padding: 1;
        overflow-y: auto;
    }
    
    /* When preview is hidden, message panel takes full width */
    #main-content:has(.preview-panel.hidden) #message-panel {
        width: 1fr;
    }
    
    /* Message list styling */
    ListView > ListItem {
        padding: 1;
    }
    
    ListView > ListItem:hover {
        background: $surface;
    }
    
    ListView > ListItem.--highlight {
        background: $primary 20%;
    }
    
    .message-item-unread {
        text-style: bold;
        color: $text;
    }
    
    .message-item-read {
        color: $text-muted;
    }
    
    /* Folder list styling */
    #folder-list ListItem {
        padding: 1;
    }
    
    #folder-list ListItem:hover {
        background: $surface;
    }
    
    #folder-list ListItem.--highlight {
        background: $primary 20%;
    }
    
    /* Search bar */
    #search-bar {
        border: wide $primary;
        margin: 1;
    }
    
    /* Message container */
    #message-container {
        padding: 1;
        background: $background;
    }
    
    #message-header {
        border-bottom: wide $primary;
        padding: 1;
        background: $surface;
    }
    
    .header-line {
        margin: 1;
    }
    
    #message-body {
        height: 1fr;
        padding: 1;
        background: $background;
    }
    
    #attachments {
        border-top: wide $primary;
        padding: 1;
        background: $surface;
    }
    
    .attachment {
        margin: 1;
        color: $accent;
    }
    
    /* Compose screen */
    #compose-container {
        padding: 1;
        background: $background;
    }
    
    .screen-title {
        text-style: bold;
        margin: 1;
        color: $accent;
        text-align: center;
    }
    
    .field-label {
        margin-top: 1;
        text-style: bold;
        color: $text;
    }
    
    #button-bar {
        align: right;
        margin-top: 1;
    }
    
    /* Settings */
    #settings-container {
        padding: 1;
        background: $background;
    }
    
    .hidden {
        display: none;
    }
    
    #create-email-container {
        padding: 1;
        background: $background;
    }
    
    #configure-smtp-container {
        padding: 1;
        background: $background;
    }
    
    /* Status bar */
    #status-bar {
        border-top: wide $primary;
        padding: 1;
        background: $surface;
        height: 3;
    }
    
    /* Status indicators */
    .status-indicator {
        margin: 1;
        padding: 1;
    }
    
    .status-connected {
        color: $success;
    }
    
    .status-disconnected {
        color: $error;
    }
    
    .status-loading {
        color: $warning;
    }
    
    /* Error and hints */
    .error {
        color: $error;
        text-style: bold;
    }
    
    .hint {
        color: $text-muted;
        font-style: italic;
        margin-bottom: 1;
    }
    
    .separator {
        height: 1;
        border-bottom: wide $primary;
        margin: 1;
    }
    
    .account-info {
        margin: 1;
        padding: 1;
        background: $surface;
    }
    
    .account-button {
        margin-left: 2;
        margin-bottom: 1;
    }
    
    /* Unread badge */
    .unread-badge {
        background: $primary;
        color: $text;
        padding: 0 1;
        border-radius: 1;
        text-style: bold;
    }
    
    /* Attachment indicator */
    .attachment-indicator {
        color: $accent;
    }
    
    /* Star indicator */
    .star-indicator {
        color: $warning;
    }
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config_manager = ConfigManager()
        self.provider: Optional[EmailProvider] = None
        self._initialize_provider()
    
    def initialize_provider(self):
        """Initialize email provider from config"""
        accounts = self.config_manager.get_accounts()
        if accounts:
            # Use the first account for now
            account = accounts[0]
            provider_type = account.get("provider", "imap")
            if provider_type == "nylas":
                self.provider = NylasProvider(account)
            elif provider_type == "local":
                self.provider = LocalProvider(account)
            else:
                self.provider = IMAPProvider(account)
        else:
            self.provider = None
    
    def _initialize_provider(self):
        """Private alias for backward compatibility"""
        self.initialize_provider()
    
    def compose(self) -> ComposeResult:
        """Compose the initial screen"""
        if self.provider:
            yield InboxScreen(self.provider, id="inbox")
        else:
            # No accounts configured, show settings
            yield SettingsScreen(self.config_manager, id="settings")
    
    def on_mount(self) -> None:
        """Called when app is mounted"""
        if self.provider:
            # Try to connect
            self.connect_provider()
    
    async def connect_provider(self):
        """Connect to email provider"""
        if self.provider:
            success = await self.provider.connect()
            if not success:
                self.push_screen("settings")
    
    def push_screen(self, screen: str, context: any = None) -> None:
        """Push a screen with context"""
        if screen == "inbox":
            if not self.provider:
                self._initialize_provider()
            if self.provider:
                super().push_screen(InboxScreen(self.provider, id="inbox"))
        elif screen == "message_view":
            if isinstance(context, Email) and self.provider:
                super().push_screen(MessageViewScreen(context, self.provider, id="message_view"))
        elif screen == "compose":
            if self.provider:
                kwargs = {}
                if isinstance(context, dict):
                    kwargs = context
                super().push_screen(ComposeScreen(self.provider, id="compose", **kwargs))
        elif screen == "settings":
            super().push_screen(SettingsScreen(self.config_manager, id="settings"))
        elif screen == "create_local_email":
            super().push_screen(CreateLocalEmailScreen(self.config_manager, id="create_local_email"))
        elif screen == "configure_smtp":
            if isinstance(context, str):  # account_id
                super().push_screen(ConfigureSMTPScreen(self.config_manager, context, id="configure_smtp"))

