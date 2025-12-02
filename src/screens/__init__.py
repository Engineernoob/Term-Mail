"""Application screens"""

from .inbox import InboxScreen
from .message_view import MessageViewScreen
from .compose import ComposeScreen
from .settings import SettingsScreen
from .create_local_email import CreateLocalEmailScreen
from .configure_smtp import ConfigureSMTPScreen

__all__ = ["InboxScreen", "MessageViewScreen", "ComposeScreen", "SettingsScreen", "CreateLocalEmailScreen", "ConfigureSMTPScreen"]

