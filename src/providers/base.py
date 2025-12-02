"""Abstract base class for email providers"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ..models.email import Email, Attachment
from ..models.folder import Folder


class EmailProvider(ABC):
    """Abstract base class for email providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connected = False
    
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the email service"""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Disconnect from the email service"""
        pass
    
    @abstractmethod
    async def fetch_emails(
        self,
        folder: str = "INBOX",
        limit: int = 50,
        offset: int = 0
    ) -> List[Email]:
        """Fetch emails from a folder"""
        pass
    
    @abstractmethod
    async def get_email(self, email_id: str) -> Optional[Email]:
        """Get a specific email by ID"""
        pass
    
    @abstractmethod
    async def send_email(
        self,
        to_addresses: List[str],
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        cc_addresses: Optional[List[str]] = None,
        bcc_addresses: Optional[List[str]] = None,
        attachments: Optional[List[Attachment]] = None,
        reply_to_id: Optional[str] = None
    ) -> bool:
        """Send an email"""
        pass
    
    @abstractmethod
    async def get_folders(self) -> List[Folder]:
        """Get list of folders"""
        pass
    
    @abstractmethod
    async def mark_read(self, email_id: str, read: bool = True) -> bool:
        """Mark an email as read or unread"""
        pass
    
    @abstractmethod
    async def delete_email(self, email_id: str) -> bool:
        """Delete an email"""
        pass
    
    @abstractmethod
    async def search_emails(
        self,
        query: str,
        folder: Optional[str] = None,
        limit: int = 50
    ) -> List[Email]:
        """Search for emails"""
        pass
    
    @abstractmethod
    async def get_attachment(
        self,
        email_id: str,
        attachment_id: str
    ) -> Optional[Attachment]:
        """Get attachment data"""
        pass

