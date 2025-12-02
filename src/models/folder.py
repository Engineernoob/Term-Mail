"""Folder model"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Folder:
    """Email folder model"""
    name: str
    display_name: str
    unread_count: int = 0
    total_count: int = 0
    id: Optional[str] = None
    
    def __post_init__(self):
        if not self.display_name:
            self.display_name = self.name

