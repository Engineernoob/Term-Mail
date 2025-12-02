"""Email message model"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class Attachment:
    """Email attachment"""
    filename: str
    content_type: str
    size: int
    data: Optional[bytes] = None
    id: Optional[str] = None


@dataclass
class Email:
    """Email message model"""
    id: str
    subject: str
    from_address: str
    to_addresses: List[str]
    cc_addresses: List[str] = None
    bcc_addresses: List[str] = None
    date: datetime = None
    body_text: str = ""
    body_html: str = ""
    attachments: List[Attachment] = None
    is_read: bool = False
    is_starred: bool = False
    thread_id: Optional[str] = None
    folder: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.cc_addresses is None:
            self.cc_addresses = []
        if self.bcc_addresses is None:
            self.bcc_addresses = []
        if self.attachments is None:
            self.attachments = []
        if self.date is None:
            self.date = datetime.now()
    
    @property
    def from_name(self) -> str:
        """Extract name from email address if present"""
        if "<" in self.from_address:
            return self.from_address.split("<")[0].strip().strip('"')
        return self.from_address.split("@")[0]
    
    @property
    def from_email(self) -> str:
        """Extract email address"""
        if "<" in self.from_address:
            return self.from_address.split("<")[1].strip(">")
        return self.from_address
    
    @property
    def preview(self) -> str:
        """Get a preview of the email body"""
        preview_text = self.body_text or self.body_html
        if len(preview_text) > 100:
            return preview_text[:97] + "..."
        return preview_text

