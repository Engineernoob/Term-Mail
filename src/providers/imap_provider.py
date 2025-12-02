"""IMAP/SMTP email provider implementation"""

import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
from datetime import datetime
import ssl
from ..models.email import Email, Attachment
from ..models.folder import Folder
from ..providers.base import EmailProvider
from ..utils.html_parser import html_to_text


class IMAPProvider(EmailProvider):
    """IMAP/SMTP email provider"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.imap: Optional[imaplib.IMAP4_SSL] = None
        self.smtp: Optional[smtplib.SMTP] = None
        self.email_address = config.get("email")
        self.password = config.get("password")
        self.imap_server = config.get("imap_server")
        self.imap_port = config.get("imap_port", 993)
        self.smtp_server = config.get("smtp_server")
        self.smtp_port = config.get("smtp_port", 587)
        self.use_tls = config.get("use_tls", True)
    
    async def connect(self) -> bool:
        """Connect to IMAP server"""
        try:
            # Connect to IMAP
            context = ssl.create_default_context()
            self.imap = imaplib.IMAP4_SSL(
                self.imap_server,
                self.imap_port,
                ssl_context=context
            )
            self.imap.login(self.email_address, self.password)
            self.connected = True
            return True
        except Exception as e:
            print(f"IMAP connection error: {e}")
            self.connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from servers"""
        if self.imap:
            try:
                self.imap.close()
                self.imap.logout()
            except:
                pass
            self.imap = None
        
        if self.smtp:
            try:
                self.smtp.quit()
            except:
                pass
            self.smtp = None
        
        self.connected = False
    
    def _parse_email(self, msg_data: bytes, email_id: str) -> Email:
        """Parse raw email message"""
        msg = email.message_from_bytes(msg_data)
        
        # Parse headers
        subject = msg.get("Subject", "(No Subject)")
        from_addr = msg.get("From", "")
        to_addrs = msg.get("To", "")
        cc_addrs = msg.get("Cc", "")
        bcc_addrs = msg.get("Bcc", "")
        date_str = msg.get("Date")
        
        # Parse date
        try:
            if date_str:
                date_tuple = email.utils.parsedate_tz(date_str)
                if date_tuple:
                    date = datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
                else:
                    date = datetime.now()
            else:
                date = datetime.now()
        except:
            date = datetime.now()
        
        # Parse addresses
        to_list = [addr.strip() for addr in to_addrs.split(",")] if to_addrs else []
        cc_list = [addr.strip() for addr in cc_addrs.split(",")] if cc_addrs else []
        bcc_list = [addr.strip() for addr in bcc_addrs.split(",")] if bcc_addrs else []
        
        # Parse body
        body_text = ""
        body_html = ""
        attachments = []
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))
                
                if "attachment" in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        payload = part.get_payload(decode=True)
                        attachments.append(Attachment(
                            filename=filename,
                            content_type=content_type,
                            size=len(payload) if payload else 0,
                            data=payload,
                            id=f"{email_id}_{len(attachments)}"
                        ))
                elif content_type == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        body_text = payload.decode('utf-8', errors='ignore')
                elif content_type == "text/html":
                    payload = part.get_payload(decode=True)
                    if payload:
                        body_html = payload.decode('utf-8', errors='ignore')
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                content_type = msg.get_content_type()
                if content_type == "text/html":
                    body_html = payload.decode('utf-8', errors='ignore')
                else:
                    body_text = payload.decode('utf-8', errors='ignore')
        
        # Convert HTML to text if needed
        if body_html and not body_text:
            body_text = html_to_text(body_html)
        
        # Check read status (IMAP doesn't directly provide this, we'll use SEEN flag)
        flags = msg.get("X-GM-LABELS", "") or ""
        is_read = "\\Seen" in str(msg.get("X-GM-LABELS", "")) or "\\Seen" in str(msg.get("Flags", ""))
        
        return Email(
            id=email_id,
            subject=subject,
            from_address=from_addr,
            to_addresses=to_list,
            cc_addresses=cc_list,
            bcc_addresses=bcc_list,
            date=date,
            body_text=body_text,
            body_html=body_html,
            attachments=attachments,
            is_read=is_read
        )
    
    async def fetch_emails(
        self,
        folder: str = "INBOX",
        limit: int = 50,
        offset: int = 0
    ) -> List[Email]:
        """Fetch emails from a folder"""
        if not self.connected or not self.imap:
            return []
        
        try:
            # Select folder
            self.imap.select(folder)
            
            # Search for all emails
            typ, message_ids = self.imap.search(None, "ALL")
            if typ != "OK":
                return []
            
            email_ids = message_ids[0].split()
            # Reverse to get newest first, then apply limit and offset
            email_ids = email_ids[::-1][offset:offset + limit]
            
            emails = []
            for email_id in email_ids:
                typ, msg_data = self.imap.fetch(email_id, "(RFC822)")
                if typ == "OK" and msg_data[0]:
                    email_obj = self._parse_email(msg_data[0][1], email_id.decode())
                    emails.append(email_obj)
            
            return emails
        except Exception as e:
            print(f"Error fetching emails: {e}")
            return []
    
    async def get_email(self, email_id: str) -> Optional[Email]:
        """Get a specific email by ID"""
        if not self.connected or not self.imap:
            return None
        
        try:
            # Select INBOX (we might need to search across folders)
            self.imap.select("INBOX")
            typ, msg_data = self.imap.fetch(email_id.encode(), "(RFC822)")
            if typ == "OK" and msg_data[0]:
                return self._parse_email(msg_data[0][1], email_id)
            return None
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
        try:
            # Create message
            if html_body or attachments:
                msg = MIMEMultipart("alternative")
            else:
                msg = MIMEText(body, "plain")
            
            msg["From"] = self.email_address
            msg["To"] = ", ".join(to_addresses)
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
                self.smtp.login(self.email_address, self.password)
            
            recipients = to_addresses.copy()
            if cc_addresses:
                recipients.extend(cc_addresses)
            if bcc_addresses:
                recipients.extend(bcc_addresses)
            
            self.smtp.send_message(msg, to_addrs=recipients)
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    async def get_folders(self) -> List[Folder]:
        """Get list of folders"""
        if not self.connected or not self.imap:
            return []
        
        try:
            typ, folders = self.imap.list()
            if typ != "OK":
                return []
            
            folder_list = []
            for folder_data in folders:
                # Parse folder name from IMAP response
                folder_str = folder_data.decode()
                # Extract folder name (format: '(\\HasNoChildren) "/" "INBOX"')
                parts = folder_str.split('"')
                if len(parts) >= 3:
                    folder_name = parts[-2]
                    folder_list.append(Folder(
                        name=folder_name,
                        display_name=folder_name.replace("/", " ").title(),
                        id=folder_name
                    ))
            
            return folder_list
        except Exception as e:
            print(f"Error getting folders: {e}")
            return []
    
    async def mark_read(self, email_id: str, read: bool = True) -> bool:
        """Mark an email as read or unread"""
        if not self.connected or not self.imap:
            return False
        
        try:
            flag = "\\Seen" if read else "-\\Seen"
            self.imap.store(email_id.encode(), "+FLAGS", flag.encode())
            return True
        except Exception as e:
            print(f"Error marking email: {e}")
            return False
    
    async def delete_email(self, email_id: str) -> bool:
        """Delete an email"""
        if not self.connected or not self.imap:
            return False
        
        try:
            self.imap.store(email_id.encode(), "+FLAGS", "\\Deleted")
            self.imap.expunge()
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
        if not self.connected or not self.imap:
            return []
        
        try:
            search_folder = folder or "INBOX"
            self.imap.select(search_folder)
            
            # Search for emails containing query in subject or body
            typ, message_ids = self.imap.search(None, f'(OR SUBJECT "{query}" BODY "{query}")')
            if typ != "OK":
                return []
            
            email_ids = message_ids[0].split()[:limit]
            emails = []
            for email_id in email_ids:
                typ, msg_data = self.imap.fetch(email_id, "(RFC822)")
                if typ == "OK" and msg_data[0]:
                    email_obj = self._parse_email(msg_data[0][1], email_id.decode())
                    emails.append(email_obj)
            
            return emails
        except Exception as e:
            print(f"Error searching emails: {e}")
            return []

    async def get_attachment(
        self,
        email_id: str,
        attachment_id: str
    ) -> Optional[Attachment]:
        """Get attachment data"""
        # For IMAP, attachment data is already included in the email
        email_obj = await self.get_email(email_id)
        if email_obj:
            for att in email_obj.attachments:
                if att.id == attachment_id:
                    return att
        return None

