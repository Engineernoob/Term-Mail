"""Configuration management"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional


class ConfigManager:
    """Manages application configuration and account storage"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.accounts_file = self.config_dir / "accounts.json"
        self._accounts: List[Dict[str, Any]] = []
        self._load_accounts()
    
    def _load_accounts(self):
        """Load accounts from file"""
        if self.accounts_file.exists():
            try:
                with open(self.accounts_file, 'r') as f:
                    self._accounts = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._accounts = []
        else:
            self._accounts = []
    
    def _save_accounts(self):
        """Save accounts to file"""
        try:
            with open(self.accounts_file, 'w') as f:
                json.dump(self._accounts, f, indent=2)
        except IOError as e:
            raise RuntimeError(f"Failed to save accounts: {e}")
    
    def add_account(self, account: Dict[str, Any]) -> str:
        """
        Add a new account.
        
        Args:
            account: Account configuration dictionary
            
        Returns:
            Account ID
        """
        account_id = account.get("id") or f"account_{len(self._accounts) + 1}"
        account["id"] = account_id
        
        # Set default values
        if "provider" not in account:
            account["provider"] = "imap"
        if "name" not in account:
            account["name"] = account.get("email", account_id)
        
        self._accounts.append(account)
        self._save_accounts()
        return account_id
    
    def get_accounts(self) -> List[Dict[str, Any]]:
        """Get all accounts"""
        return self._accounts.copy()
    
    def get_account(self, account_id: str) -> Optional[Dict[str, Any]]:
        """Get account by ID"""
        for account in self._accounts:
            if account.get("id") == account_id:
                return account.copy()
        return None
    
    def remove_account(self, account_id: str) -> bool:
        """Remove an account"""
        original_count = len(self._accounts)
        self._accounts = [acc for acc in self._accounts if acc.get("id") != account_id]
        if len(self._accounts) < original_count:
            self._save_accounts()
            return True
        return False
    
    def update_account(self, account_id: str, updates: Dict[str, Any]) -> bool:
        """Update an account"""
        for i, account in enumerate(self._accounts):
            if account.get("id") == account_id:
                self._accounts[i].update(updates)
                self._save_accounts()
                return True
        return False

