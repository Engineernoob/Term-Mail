"""Local email address management"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from ..providers.local_provider import LocalProvider


class LocalEmailManager:
    """Manages local email addresses"""
    
    def __init__(self, storage_dir: str = "data/local_emails"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.addresses_file = self.storage_dir / "addresses.json"
        self._addresses: List[Dict[str, Any]] = []
        self._load_addresses()
    
    def _load_addresses(self):
        """Load addresses from storage"""
        if self.addresses_file.exists():
            try:
                with open(self.addresses_file, 'r') as f:
                    self._addresses = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._addresses = []
        else:
            self._addresses = []
    
    def _save_addresses(self):
        """Save addresses to storage"""
        try:
            with open(self.addresses_file, 'w') as f:
                json.dump(self._addresses, f, indent=2)
        except IOError as e:
            raise RuntimeError(f"Failed to save addresses: {e}")
    
    def create_email_address(self, local_part: str, domain: str = "local") -> Dict[str, Any]:
        """
        Create a new local email address.
        
        Args:
            local_part: Local part of email (before @)
            domain: Domain part (default: "local")
            
        Returns:
            Account configuration dictionary
        """
        email_address = f"{local_part}@{domain}"
        
        # Check if address already exists
        if self.email_address_exists(email_address):
            raise ValueError(f"Email address {email_address} already exists")
        
        # Validate email format
        if "@" not in email_address or len(local_part) == 0:
            raise ValueError("Invalid email address format")
        
        # Create account config
        account = {
            "provider": "local",
            "email_address": email_address,
            "storage_dir": str(self.storage_dir),
            "name": email_address,
            # SMTP config can be added later via update_account
        }
        
        # Add to addresses list
        address_info = {
            "email_address": email_address,
            "local_part": local_part,
            "domain": domain,
            "created": str(Path().cwd())
        }
        self._addresses.append(address_info)
        self._save_addresses()
        
        return account
    
    def email_address_exists(self, email_address: str) -> bool:
        """Check if an email address already exists"""
        return any(addr.get("email_address") == email_address for addr in self._addresses)
    
    def get_email_addresses(self) -> List[str]:
        """Get list of all local email addresses"""
        return [addr.get("email_address") for addr in self._addresses]
    
    def delete_email_address(self, email_address: str) -> bool:
        """Delete a local email address and its data"""
        original_count = len(self._addresses)
        self._addresses = [addr for addr in self._addresses if addr.get("email_address") != email_address]
        
        if len(self._addresses) < original_count:
            self._save_addresses()
            
            # Delete email storage file
            email_file = self.storage_dir / f"{email_address.replace('@', '_at_')}.json"
            if email_file.exists():
                email_file.unlink()
            
            return True
        return False
    
    def get_provider_for_address(self, email_address: str) -> Optional[LocalProvider]:
        """Get a LocalProvider instance for an email address"""
        if not self.email_address_exists(email_address):
            return None
        
        config = {
            "provider": "local",
            "email_address": email_address,
            "storage_dir": str(self.storage_dir)
        }
        return LocalProvider(config)

