"""Local email provider for custom email addresses"""

import json
import uuid
import smtplib
import ssl
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formatdate
from ..models.email import Email, Attachment
from ..models.folder import Folder
from ..providers.base import EmailProvider
from ..utils.html_parser import html_to_text


class LocalProvider(EmailProvider):
    """Local email provider that stores emails in the filesystem"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.email_address = config.get("email_address", "")
        self.storage_dir = Path(config.get("storage_dir", "data/local_emails"))
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.emails_file = self.storage_dir / f"{self.email_address.replace('@', '_at_')}.json"
        self._emails: Dict[str, Dict[str, Any]] = {}
        
        # SMTP configuration for sending to external addresses
        self.smtp_server = config.get("smtp_server")
        self.smtp_port = config.get("smtp_port", 587)
        self.smtp_username = config.get("smtp_username")
        self.smtp_password = config.get("smtp_password")
        self.use_tls = config.get("use_tls", True)
        self.smtp: Optional[smtplib.SMTP] = None
        
        self._load_emails()
    
    def _load_emails(self):
        """Load emails from storage"""
        if self.emails_file.exists():
            try:
                with open(self.emails_file, 'r') as f:
                    data = json.load(f)
                    self._emails = {k: v for k, v in data.items()}
            except (json.JSONDecodeError, IOError):
                self._emails = {}
        else:
            self._emails = {}
    
    def _save_emails(self):
        """Save emails to storage"""
        try:
            with open(self.emails_file, 'w') as f:
                json.dump(self._emails, f, indent=2, default=str)
        except IOError as e:
            print(f"Error saving emails: {e}")
    
    def _dict_to_email(self, email_dict: Dict[str, Any]) -> Email:
        """Convert dictionary to Email object"""
        attachments = []
        if email_dict.get("attachments"):
            for att_dict in email_dict["attachments"]:
                attachments.append(Attachment(
                    filename=att_dict.get("filename", ""),
                    content_type=att_dict.get("content_type", ""),
                    size=att_dict.get("size", 0),
                    data=bytes(att_dict.get("data", [])) if att_dict.get("data") else None,
                    id=att_dict.get("id")
                ))
        
        date_str = email_dict.get("date")
        if isinstance(date_str, str):
            try:
                date = datetime.fromisoformat(date_str)
            except:
                date = datetime.now()
        elif isinstance(date_str, datetime):
            date = date_str
        else:
            date = datetime.now()
        
        return Email(
            id=email_dict.get("id", ""),
            subject=email_dict.get("subject", ""),
            from_address=email_dict.get("from_address", ""),
            to_addresses=email_dict.get("to_addresses", []),
            cc_addresses=email_dict.get("cc_addresses", []),
            bcc_addresses=email_dict.get("bcc_addresses", []),
            date=date,
            body_text=email_dict.get("body_text", ""),
            body_html=email_dict.get("body_html", ""),
            attachments=attachments,
            is_read=email_dict.get("is_read", False),
            is_starred=email_dict.get("is_starred", False),
            folder=email_dict.get("folder", "INBOX")
        )
    
    def _email_to_dict(self, email_obj: Email) -> Dict[str, Any]:
        """Convert Email object to dictionary"""
        attachments = []
        for att in email_obj.attachments:
            attachments.append({
                "filename": att.filename,
                "content_type": att.content_type,
                "size": att.size,
                "data": list(att.data) if att.data else None,
                "id": att.id
            })
        
        return {
            "id": email_obj.id,
            "subject": email_obj.subject,
            "from_address": email_obj.from_address,
            "to_addresses": email_obj.to_addresses,
            "cc_addresses": email_obj.cc_addresses,
            "bcc_addresses": email_obj.bcc_addresses,
            "date": email_obj.date.isoformat(),
            "body_text": email_obj.body_text,
            "body_html": email_obj.body_html,
            "attachments": attachments,
            "is_read": email_obj.is_read,
            "is_starred": email_obj.is_starred,
            "folder": email_obj.folder or "INBOX"
        }
    
    async def connect(self) -> bool:
        """Connect to local storage (always succeeds)"""
        self.connected = True
        return True
    
    async def disconnect(self):
        """Disconnect from local storage"""
        self._save_emails()
        if self.smtp:
            try:
                self.smtp.quit()
            except:
                pass
            self.smtp = None
        self.connected = False
    
    async def fetch_emails(
        self,
        folder: str = "INBOX",
        limit: int = 50,
        offset: int = 0
    ) -> List[Email]:
        """Fetch emails from a folder"""
        if not self.connected:
            return []
        
        emails = []
        for email_dict in self._emails.values():
            if email_dict.get("folder", "INBOX") == folder:
                emails.append(self._dict_to_email(email_dict))
        
        # Sort by date, newest first
        emails.sort(key=lambda e: e.date, reverse=True)
        
        # Apply limit and offset
        return emails[offset:offset + limit]
    
    async def get_email(self, email_id: str) -> Optional[Email]:
        """Get a specific email by ID"""
        if not self.connected:
            return None
        
        email_dict = self._emails.get(email_id)
        if email_dict:
            return self._dict_to_email(email_dict)
        return None
    
    def _is_local_address(self, email_address: str) -> bool:
        """Check if an email address is a local address"""
        local_file = self.storage_dir / f"{email_address.replace('@', '_at_')}.json"
        return local_file.exists()
    
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
        """Send an email (store it locally for local addresses, or send via SMTP for external)"""
        if not self.connected:
            return False
        
        try:
            # Create email ID
            email_id = str(uuid.uuid4())
            
            # Create email object
            email_obj = Email(
                id=email_id,
                subject=subject,
                from_address=self.email_address,
                to_addresses=to_addresses,
                cc_addresses=cc_addresses or [],
                bcc_addresses=bcc_addresses or [],
                date=datetime.now(),
                body_text=body,
                body_html=html_body or "",
                attachments=attachments or [],
                is_read=False,
                folder="Sent"
            )
            
            # Separate local and external recipients
            local_recipients = []
            external_recipients = []
            
            for addr in to_addresses:
                if self._is_local_address(addr):
                    local_recipients.append(addr)
                else:
                    external_recipients.append(addr)
            
            # Send to external addresses via SMTP if configured
            if external_recipients and self.smtp_server and self.smtp_username and self.smtp_password:
                try:
                    # Create MIME message
                    if html_body or attachments:
                        msg = MIMEMultipart("alternative")
                    else:
                        msg = MIMEText(body, "plain")
                    
                    msg["From"] = self.email_address
                    msg["To"] = ", ".join(external_recipients)
                    msg["Subject"] = subject
                    
                    if cc_addresses:
                        msg["Cc"] = ", ".join(cc_addresses)
                    
                    if html_body:
                        part1 = MIMEText(body, "plain")
                        part2 = MIMEText(html_body, "html")
                        msg.attach(part1)
                        msg.attach(part2)
                    elif isinstance(msg, MIMEMultipart):
                        msg.attach(MIMEText(body, "plain"))
                    
                    # Add attachments
                    if attachments:
                        for att in attachments:
                            part = MIMEBase("application", "octet-stream")
                            part.set_payload(att.data)
                            encoders.encode_base64(part)
                            part.add_header(
                                "Content-Disposition",
                                f"attachment; filename= {att.filename}"
                            )
                            msg.attach(part)
                    
                    # Connect to SMTP and send
                    if not self.smtp:
                        self.smtp = smtplib.SMTP(self.smtp_server, self.smtp_port)
                        if self.use_tls:
                            self.smtp.starttls()
                        self.smtp.login(self.smtp_username, self.smtp_password)
                    
                    recipients = external_recipients.copy()
                    if cc_addresses:
                        recipients.extend(cc_addresses)
                    if bcc_addresses:
                        recipients.extend(bcc_addresses)
                    
                    self.smtp.send_message(msg, to_addrs=recipients)
                except Exception as e:
                    print(f"Error sending via SMTP: {e}")
                    # Continue to store locally even if SMTP fails
            
            # Store in Sent folder
            self._emails[email_id] = self._email_to_dict(email_obj)
            
            # Deliver to local recipients
            for to_addr in local_recipients:
                local_file = self.storage_dir / f"{to_addr.replace('@', '_at_')}.json"
                if local_file.exists():
                    # This is a local address, deliver the email
                    try:
                        with open(local_file, 'r') as f:
                            recipient_emails = json.load(f)
                    except:
                        recipient_emails = {}
                    
                    # Create a copy for the recipient
                    recipient_email = self._email_to_dict(email_obj)
                    recipient_email["id"] = str(uuid.uuid4())
                    recipient_email["folder"] = "INBOX"
                    recipient_emails[recipient_email["id"]] = recipient_email
                    
                    with open(local_file, 'w') as f:
                        json.dump(recipient_emails, f, indent=2, default=str)
            
            self._save_emails()
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    async def get_folders(self) -> List[Folder]:
        """Get list of folders"""
        folders = {}
        
        # Count emails in each folder
        for email_dict in self._emails.values():
            folder_name = email_dict.get("folder", "INBOX")
            if folder_name not in folders:
                folders[folder_name] = {"total": 0, "unread": 0}
            folders[folder_name]["total"] += 1
            if not email_dict.get("is_read", False):
                folders[folder_name]["unread"] += 1
        
        # Create Folder objects
        folder_list = []
        default_folders = ["INBOX", "Sent", "Drafts", "Trash"]
        
        for folder_name in default_folders:
            folder_list.append(Folder(
                name=folder_name,
                display_name=folder_name,
                id=folder_name,
                unread_count=folders.get(folder_name, {}).get("unread", 0),
                total_count=folders.get(folder_name, {}).get("total", 0)
            ))
        
        # Add any other folders found
        for folder_name in folders:
            if folder_name not in default_folders:
                folder_list.append(Folder(
                    name=folder_name,
                    display_name=folder_name,
                    id=folder_name,
                    unread_count=folders[folder_name]["unread"],
                    total_count=folders[folder_name]["total"]
                ))
        
        return folder_list
    
    async def mark_read(self, email_id: str, read: bool = True) -> bool:
        """Mark an email as read or unread"""
        if not self.connected:
            return False
        
        if email_id in self._emails:
            self._emails[email_id]["is_read"] = read
            self._save_emails()
            return True
        return False
    
    async def delete_email(self, email_id: str) -> bool:
        """Delete an email (move to Trash)"""
        if not self.connected:
            return False
        
        if email_id in self._emails:
            self._emails[email_id]["folder"] = "Trash"
            self._save_emails()
            return True
        return False
    
    async def search_emails(
        self,
        query: str,
        folder: Optional[str] = None,
        limit: int = 50
    ) -> List[Email]:
        """Search for emails"""
        if not self.connected:
            return []
        
        query_lower = query.lower()
        results = []
        
        for email_dict in self._emails.values():
            if folder and email_dict.get("folder") != folder:
                continue
            
            # Search in subject, body, and from address
            if (query_lower in email_dict.get("subject", "").lower() or
                query_lower in email_dict.get("body_text", "").lower() or
                query_lower in email_dict.get("from_address", "").lower()):
                results.append(self._dict_to_email(email_dict))
        
        # Sort by date, newest first
        results.sort(key=lambda e: e.date, reverse=True)
        
        return results[:limit]
    
    async def get_attachment(
        self,
        email_id: str,
        attachment_id: str
    ) -> Optional[Attachment]:
        """Get attachment data"""
        email_obj = await self.get_email(email_id)
        if email_obj:
            for att in email_obj.attachments:
                if att.id == attachment_id:
                    return att
        return None
    
    def receive_email(self, email_obj: Email):
        """Receive an email (called when email is delivered to this address)"""
        if not self.connected:
            return
        
        email_dict = self._email_to_dict(email_obj)
        email_dict["folder"] = "INBOX"
        self._emails[email_obj.id] = email_dict
        self._save_emails()

