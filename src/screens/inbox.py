"""Inbox screen"""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Header, Footer, Label
from textual import work
from typing import Optional
from ..widgets.message_list import MessageList
from ..widgets.folder_list import FolderList
from ..widgets.search_bar import SearchBar
from ..widgets.status_bar import StatusBar
from ..widgets.message_preview import MessagePreview
from ..models.email import Email
from ..models.folder import Folder
from ..providers.base import EmailProvider


class InboxScreen(Screen):
    """Main inbox screen"""
    
    BINDINGS = [
        ("n", "compose", "New Email"),
        ("r", "reply", "Reply"),
        ("f", "forward", "Forward"),
        ("d", "delete", "Delete"),
        ("u", "mark_unread", "Mark Unread"),
        ("m", "mark_read", "Mark Read"),
        ("/", "search", "Search"),
        ("enter", "open_message", "Open Message"),
        ("p", "toggle_preview", "Toggle Preview"),
        ("c", "create_local", "Create Local Email"),
        ("s", "settings", "Settings"),
        ("q", "quit", "Quit"),
    ]
    
    def __init__(self, provider: EmailProvider, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.provider = provider
        self.current_folder = "INBOX"
        self.current_email: Optional[Email] = None
        self.search_mode = False
        self.preview_visible = True
    
    def compose(self) -> ComposeResult:
        """Compose the screen layout"""
        yield Header(show_clock=True)
        
        with Horizontal():
            with Vertical(id="sidebar", classes="sidebar"):
                yield Label("📁 Folders", classes="section-title")
                yield FolderList(id="folder-list")
            
            with Horizontal(id="main-content"):
                with Vertical(id="message-panel"):
                    yield Label("🔍 Search", classes="section-title")
                    yield SearchBar(id="search-bar")
                    yield Label("📧 Messages", classes="section-title")
                    yield MessageList(id="message-list")
                    yield StatusBar(id="status-bar")
                
                with Vertical(id="preview-panel", classes="preview-panel"):
                    yield Label("👁 Preview", classes="section-title")
                    yield MessagePreview(id="message-preview")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Called when screen is mounted"""
        status_bar = self.query_one("#status-bar", StatusBar)
        provider_type = type(self.provider).__name__.replace("Provider", "")
        status_bar.set_provider(provider_type)
        status_bar.set_connected(self.provider.connected if self.provider else False)
        
        self.load_folders()
        self.load_messages()
    
    @work(exclusive=True)
    async def load_folders(self):
        """Load folders from provider"""
        status_bar = self.query_one("#status-bar", StatusBar)
        status_bar.set_message("Loading folders...")
        try:
            folders = await self.provider.get_folders()
            folder_list = self.query_one("#folder-list", FolderList)
            folder_list.load_folders(folders)
            status_bar.clear_message()
        except Exception as e:
            status_bar.set_message(f"Error loading folders: {str(e)}")
    
    @work(exclusive=True)
    async def load_messages(self, folder: str = None):
        """Load messages from current folder"""
        folder = folder or self.current_folder
        self.current_folder = folder
        
        status_bar = self.query_one("#status-bar", StatusBar)
        status_bar.set_message(f"Loading {folder}...")
        try:
            messages = await self.provider.fetch_emails(folder=folder, limit=50)
            message_list = self.query_one("#message-list", MessageList)
            message_list.load_messages(messages)
            status_bar.set_message(f"Loaded {len(messages)} messages")
            
            # Show first message in preview if available
            preview = self.query_one("#message-preview", MessagePreview)
            if messages:
                preview.show_email(messages[0])
                self.current_email = messages[0]
            else:
                preview.clear()
                self.current_email = None
            
            # Clear message after a delay
            self.set_timer(2.0, lambda: status_bar.clear_message())
        except Exception as e:
            status_bar.set_message(f"Error loading messages: {str(e)}")
    
    def on_folder_list_folder_selected(self, event: FolderList.FolderSelected) -> None:
        """Handle folder selection"""
        self.load_messages(event.folder.name)
    
    def on_message_list_message_selected(self, event: MessageList.MessageSelected) -> None:
        """Handle message selection"""
        self.current_email = event.email
        # Update preview pane
        preview = self.query_one("#message-preview", MessagePreview)
        preview.show_email(event.email)
    
    def on_search_bar_search_submitted(self, event: SearchBar.SearchSubmitted) -> None:
        """Handle search submission"""
        self.search_emails(event.query)
    
    @work(exclusive=True)
    async def search_emails(self, query: str):
        """Search for emails"""
        status_bar = self.query_one("#status-bar", StatusBar)
        status_bar.set_message(f"Searching for '{query}'...")
        try:
            messages = await self.provider.search_emails(query, folder=self.current_folder)
            message_list = self.query_one("#message-list", MessageList)
            message_list.load_messages(messages)
            self.search_mode = True
            
            # Show first result in preview if available
            preview = self.query_one("#message-preview", MessagePreview)
            if messages:
                preview.show_email(messages[0])
                self.current_email = messages[0]
            else:
                preview.clear()
                self.current_email = None
                status_bar.set_message("No results found")
            
            if messages:
                status_bar.set_message(f"Found {len(messages)} results")
            self.set_timer(2.0, lambda: status_bar.clear_message())
        except Exception as e:
            status_bar.set_message(f"Search error: {str(e)}")
    
    def action_compose(self):
        """Open compose screen"""
        self.app.push_screen("compose")
    
    def action_reply(self):
        """Reply to current email"""
        if self.current_email:
            self.app.push_screen("compose", {"reply_to": self.current_email})
    
    def action_forward(self):
        """Forward current email"""
        if self.current_email:
            self.app.push_screen("compose", {"forward": self.current_email})
    
    @work(exclusive=True)
    async def action_delete(self):
        """Delete current email"""
        if self.current_email:
            success = await self.provider.delete_email(self.current_email.id)
            if success:
                self.load_messages()
                self.current_email = None
    
    @work(exclusive=True)
    async def action_mark_unread(self):
        """Mark current email as unread"""
        if self.current_email:
            success = await self.provider.mark_read(self.current_email.id, read=False)
            if success:
                self.current_email.is_read = False
                message_list = self.query_one("#message-list", MessageList)
                message_list.update_message_status(self.current_email.id, False)
    
    def action_search(self):
        """Focus search bar"""
        search_bar = self.query_one("#search-bar", SearchBar)
        search_bar.focus()
    
    def action_create_local(self):
        """Create a local email address"""
        self.app.push_screen("create_local_email")
    
    def action_settings(self):
        """Open settings screen"""
        self.app.push_screen("settings")
    
    def action_mark_read(self):
        """Mark current email as read"""
        if self.current_email:
            self.action_mark_unread()  # Toggle - if unread, mark as read
            if self.current_email.is_read:
                # Actually mark as read
                self.action_mark_unread()  # This will mark as read
    
    def action_toggle_preview(self):
        """Toggle preview pane visibility"""
        preview_panel = self.query_one("#preview-panel")
        if self.preview_visible:
            preview_panel.add_class("hidden")
            self.preview_visible = False
        else:
            preview_panel.remove_class("hidden")
            self.preview_visible = True
    
    def action_open_message(self):
        """Open the selected message in full view"""
        message_list = self.query_one("#message-list", MessageList)
        email = message_list.get_selected_email()
        if email:
            self.current_email = email
            self.app.push_screen("message_view", email)
    
    def on_list_view_highlighted(self, event) -> None:
        """Handle when message is highlighted (arrow keys)"""
        # Update preview when navigating with arrow keys
        message_list = self.query_one("#message-list", MessageList)
        email = message_list.get_selected_email()
        if email:
            preview = self.query_one("#message-preview", MessagePreview)
            preview.show_email(email)
    
    def action_quit(self):
        """Quit application"""
        self.app.exit()

