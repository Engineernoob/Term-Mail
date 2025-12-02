"""Nylas email provider implementation"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from nylas import APIClient
from nylas.models import Message, Folder as NylasFolder
from ..models.email import Email, Attachment
from ..models.folder import Folder
from ..providers.base import EmailProvider
from ..utils.html_parser import html_to_text


class NylasProvider(EmailProvider):
    """Nylas API email provider"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client: Optional[APIClient] = None
        self.grant_id: Optional[str] = None
    
    async def connect(self) -> bool:
        """Connect to Nylas API"""
        try:
            access_token = self.config.get("access_token")
            if not access_token:
                return False
            
            self.client = APIClient(
                api_key=self.config.get("api_key"),
                api_uri=self.config.get("api_uri", "https://api.nylas.com")
            )
            self.grant_id = self.config.get("grant_id")
            self.connected = True
            return True
        except Exception as e:
            print(f"Nylas connection error: {e}")
            self.connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from Nylas API"""
        self.client = None
        self.connected = False
    
    def _nylas_to_email(self, nylas_message: Message) -> Email:
        """Convert Nylas Message to Email model"""
        # Parse date
        date = datetime.fromtimestamp(nylas_message.date) if nylas_message.date else datetime.now()
        
        # Get body content
        body_text = nylas_message.body if nylas_message.body else ""
        body_html = nylas_message.body if nylas_message.body else ""
        
        # Convert HTML to text if needed
        if body_html and not body_text:
            body_text = html_to_text(body_html)
        
        # Parse attachments
        attachments = []
        if nylas_message.attachments:
            for att in nylas_message.attachments:
                attachments.append(Attachment(
                    filename=att.filename or "attachment",
                    content_type=att.content_type or "application/octet-stream",
                    size=att.size or 0,
                    id=att.id
                ))
        
        return Email(
            id=nylas_message.id,
            subject=nylas_message.subject or "(No Subject)",
            from_address=nylas_message.from_[0].email if nylas_message.from_ else "",
            to_addresses=[addr.email for addr in (nylas_message.to or [])],
            cc_addresses=[addr.email for addr in (nylas_message.cc or [])],
            bcc_addresses=[addr.email for addr in (nylas_message.bcc or [])],
            date=date,
            body_text=body_text,
            body_html=body_html,
            attachments=attachments,
            is_read=not nylas_message.unread if hasattr(nylas_message, 'unread') else True,
            thread_id=nylas_message.thread_id,
            folder=nylas_message.folder_id,
            raw_data=nylas_message.dict() if hasattr(nylas_message, 'dict') else {}
        )
    
    async def fetch_emails(
        self,
        folder: str = "INBOX",
        limit: int = 50,
        offset: int = 0
    ) -> List[Email]:
        """Fetch emails from a folder"""
        if not self.connected or not self.client:
            return []
        
        try:
            query_params = {
                "limit": limit,
                "offset": offset,
            }
            
            if folder and folder != "INBOX":
                query_params["in"] = folder
            
            messages = self.client.messages.list(
                identifier=self.grant_id,
                query_params=query_params
            )
            
            return [self._nylas_to_email(msg) for msg in messages.data]
        except Exception as e:
            print(f"Error fetching emails: {e}")
            return []
    
    async def get_email(self, email_id: str) -> Optional[Email]:
        """Get a specific email by ID"""
        if not self.connected or not self.client:
            return None
        
        try:
            message = self.client.messages.find(
                identifier=self.grant_id,
                message_id=email_id
            )
            return self._nylas_to_email(message)
        except Exception as e:
            print(f"Error getting email: {e}")
            return None
    
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
        if not self.connected or not self.client:
            return False
        
        try:
            message_data = {
                "to": [{"email": addr} for addr in to_addresses],
                "subject": subject,
                "body": html_body or body,
            }
            
            if cc_addresses:
                message_data["cc"] = [{"email": addr} for addr in cc_addresses]
            if bcc_addresses:
                message_data["bcc"] = [{"email": addr} for addr in bcc_addresses]
            if reply_to_id:
                message_data["reply_to"] = [{"message_id": reply_to_id}]
            
            # Handle attachments
            if attachments:
                # Note: Nylas attachments need to be uploaded first
                # This is a simplified version
                pass
            
            self.client.messages.create(
                identifier=self.grant_id,
                request_body=message_data
            )
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    async def get_folders(self) -> List[Folder]:
        """Get list of folders"""
        if not self.connected or not self.client:
            return []
        
        try:
            folders = self.client.folders.list(identifier=self.grant_id)
            return [
                Folder(
                    name=folder.name,
                    display_name=folder.display_name or folder.name,
                    id=folder.id,
                    unread_count=getattr(folder, 'unread_count', 0),
                    total_count=getattr(folder, 'total_count', 0)
                )
                for folder in folders.data
            ]
        except Exception as e:
            print(f"Error getting folders: {e}")
            return []
    
    async def mark_read(self, email_id: str, read: bool = True) -> bool:
        """Mark an email as read or unread"""
        if not self.connected or not self.client:
            return False
        
        try:
            self.client.messages.update(
                identifier=self.grant_id,
                message_id=email_id,
                request_body={"unread": not read}
            )
            return True
        except Exception as e:
            print(f"Error marking email: {e}")
            return False
    
    async def delete_email(self, email_id: str) -> bool:
        """Delete an email"""
        if not self.connected or not self.client:
            return False
        
        try:
            self.client.messages.destroy(
                identifier=self.grant_id,
                message_id=email_id
            )
            return True
        except Exception as e:
            print(f"Error deleting email: {e}")
            return False
    
    async def search_emails(
        self,
        query: str,
        folder: Optional[str] = None,
        limit: int = 50
    ) -> List[Email]:
        """Search for emails"""
        if not self.connected or not self.client:
            return []
        
        try:
            query_params = {
                "q": query,
                "limit": limit
            }
            
            if folder:
                query_params["in"] = folder
            
            messages = self.client.messages.search(
                identifier=self.grant_id,
                query=query,
                query_params=query_params
            )
            
            return [self._nylas_to_email(msg) for msg in messages.data]
        except Exception as e:
            print(f"Error searching emails: {e}")
            return []
    
    async def get_attachment(
        self,
        email_id: str,
        attachment_id: str
    ) -> Optional[Attachment]:
        """Get attachment data"""
        if not self.connected or not self.client:
            return None
        
        try:
            attachment = self.client.attachments.find(
                identifier=self.grant_id,
                attachment_id=attachment_id
            )
            
            # Download attachment data
            attachment_data = self.client.attachments.download(
                identifier=self.grant_id,
                attachment_id=attachment_id
            )
            
            return Attachment(
                filename=attachment.filename or "attachment",
                content_type=attachment.content_type or "application/octet-stream",
                size=attachment.size or 0,
                data=attachment_data,
                id=attachment.id
            )
        except Exception as e:
            print(f"Error getting attachment: {e}")
            return None

