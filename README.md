# Term-Mail

A powerful, feature-rich terminal-based email client built with Python and Textual. Term-Mail provides a modern, keyboard-driven interface for managing your emails directly from the terminal, supporting multiple email providers including Gmail, Outlook, and custom local email addresses.

![Term-Mail](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## Table of Contents

- [Features](#features)
- [Screenshots](#screenshots)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
  - [IMAP/SMTP Setup](#imapsmtp-setup)
  - [Nylas Setup](#nylas-setup)
  - [Local Email Addresses](#local-email-addresses)
- [Usage Guide](#usage-guide)
  - [Key Bindings](#key-bindings)
  - [Navigation](#navigation)
  - [Composing Emails](#composing-emails)
  - [Managing Messages](#managing-messages)
- [Project Structure](#project-structure)
- [Architecture](#architecture)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Features

### Core Email Functionality
- ✅ **Multi-provider Support**: Connect via IMAP/SMTP, Nylas API, or use local email addresses
- ✅ **Split-View Interface**: Browse messages while viewing previews side-by-side
- ✅ **Rich Message Display**: Color-coded unread messages, status indicators, and formatted text
- ✅ **Full Email Management**: Read, compose, reply, forward, delete, and search emails
- ✅ **Folder Navigation**: Access INBOX, Sent, Drafts, Trash, and custom folders
- ✅ **Search Functionality**: Quick search across subjects, bodies, and sender addresses
- ✅ **Attachment Support**: View attachment information and download attachments
- ✅ **HTML Email Rendering**: Converts HTML emails to readable plain text

### Local Email System
- ✅ **Create Custom Addresses**: Generate your own email addresses (e.g., `alice@local`)
- ✅ **Instant Delivery**: Send emails between local addresses instantly
- ✅ **SMTP Integration**: Configure SMTP to send from local addresses to external providers
- ✅ **Persistent Storage**: All local emails stored securely on your machine

### User Interface
- ✅ **Modern Terminal UI**: Built with Textual framework for responsive, beautiful interfaces
- ✅ **Color-Coded Messages**: Visual indicators for unread, starred, and attachments
- ✅ **Status Bar**: Real-time connection status and operation feedback
- ✅ **Keyboard-Driven**: Full keyboard navigation - no mouse required
- ✅ **Preview Pane**: See message content without opening full view
- ✅ **Rich Formatting**: Beautiful typography with Rich library

## Screenshots

```
┌─────────────────────────────────────────────────────────────┐
│ Term-Mail                                   12:34 PM       │
├──────────┬──────────────────────┬──────────────────────────┤
│ Folders  │ Messages             │ Preview                  │
│          │                      │                          │
│ 📥 INBOX │ ● Alice   Meeting    │ ┌──────────────────────┐ │
│   (5)    │   Bob     Project    │ │ Preview ●            │ │
│          │ ● Carol   Update     │ │                      │ │
│ 📤 Sent  │   David   Report     │ │ From: alice@mail.com │ │
│   (12)   │ ● Eve     Reminder   │ │ To: bob@mail.com     │ │
│          │                      │ │ Subject: Meeting     │ │
│ 📝 Drafts│                      │ │                      │ │
│   (2)    │                      │ │ ──────────────────── │ │
│          │                      │ │                      │ │
│ 🗑 Trash │                      │ │ Hi Bob,              │ │
│   (0)    │                      │ │                      │ │
│          │                      │ │ Let's meet tomorrow  │ │
│          │                      │ │ at 2 PM...           │ │
│          │ Status: Connected    │ └──────────────────────┘ │
└──────────┴──────────────────────┴──────────────────────────┘
│ n:New  r:Reply  f:Forward  d:Delete  u:Unread  /:Search  q:Quit │
└──────────────────────────────────────────────────────────────────┘
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/term-mail.git
cd term-mail
```

### Step 2: Install Dependencies

```bash
pip3 install -r requirements.txt
```

Or if you prefer using a virtual environment (recommended):

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 3: Run the Application

```bash
python3 main.py
```

## Quick Start

1. **First Launch**: The app will show the Settings screen if no accounts are configured
2. **Add an Account**: 
   - Press `s` for Settings
   - Choose your provider type (IMAP/SMTP, Nylas, or Local Email)
   - Enter your credentials
3. **Start Using**: Once configured, you'll see your inbox with messages
4. **Navigate**: Use arrow keys to move through messages, `Enter` to open, `/` to search

## Configuration

Account configurations are stored in `config/accounts.json`. The application automatically creates this directory and file on first run.

### IMAP/SMTP Setup

Connect to any email provider that supports IMAP/SMTP:

**Gmail Example:**
- Email: `your.email@gmail.com`
- Password: Your Gmail password or App Password (recommended)
- IMAP Server: `imap.gmail.com`
- IMAP Port: `993`
- SMTP Server: `smtp.gmail.com`
- SMTP Port: `587`

**Outlook Example:**
- Email: `your.email@outlook.com`
- Password: Your Outlook password
- IMAP Server: `outlook.office365.com`
- IMAP Port: `993`
- SMTP Server: `smtp.office365.com`
- SMTP Port: `587`

**Security Note**: For Gmail, you may need to:
1. Enable "Less secure app access" (not recommended), OR
2. Use an [App Password](https://support.google.com/accounts/answer/185833) (recommended)

### Nylas Setup

Nylas provides a unified API for accessing multiple email providers:

1. **Sign Up**: Create an account at [Nylas Dashboard](https://dashboard.nylas.com)
2. **Create Application**: Create a new application in the dashboard
3. **Get Credentials**: Copy your API Key, Access Token, and Grant ID
4. **Configure**: Enter these credentials in the Settings screen

**Supported Providers via Nylas:**
- Gmail
- Outlook/Office 365
- Yahoo Mail
- iCloud Mail
- And many more...

### Local Email Addresses

Create your own email addresses that work entirely on your machine:

#### Creating a Local Email Address

1. **From Inbox**: Press `c` or go to Settings → Create Local Email
2. **Enter Details**:
   - Local Part: Your username (e.g., `alice`)
   - Domain: Domain name (default: `local`)
   - Result: `alice@local`

#### Configuring SMTP for External Sending

To send emails from your local address to external addresses (Gmail, Outlook, etc.):

1. **During Creation**: Fill in SMTP settings when creating the address
2. **Later Configuration**: Go to Settings → Configure SMTP for your local address

**SMTP Configuration Example:**
- SMTP Server: `smtp.gmail.com`
- SMTP Port: `587`
- SMTP Username: Your Gmail address
- SMTP Password: Your Gmail password or App Password

**How It Works:**
- Emails to local addresses (`@local`) are delivered instantly
- Emails to external addresses are sent through your configured SMTP server
- Your local address appears as the "From" address

## Usage Guide

### Key Bindings

#### Global Shortcuts
- `q` - Quit application
- `s` - Open Settings
- `?` - Show help (if implemented)

#### Inbox Navigation
- `↑` / `↓` - Navigate message list
- `Enter` - Open selected message in full view
- `p` - Toggle preview pane visibility
- `/` - Focus search bar

#### Message Actions
- `n` - Compose new email
- `r` - Reply to selected message
- `f` - Forward selected message
- `d` - Delete selected message
- `u` - Mark as unread (toggle)
- `m` - Mark as read

#### Folder Navigation
- Use arrow keys in folder list to switch folders
- Click or press Enter on a folder to view its messages

#### Compose Screen
- `Ctrl+S` - Send email
- `Escape` - Cancel and return to inbox
- `Tab` - Navigate between fields

#### Message View Screen
- `r` - Reply
- `f` - Forward
- `d` - Delete
- `u` - Mark as unread
- `b` - Back to inbox

### Navigation

#### Browsing Messages
1. Use arrow keys to navigate the message list
2. Preview pane automatically updates as you navigate
3. Press `Enter` to open full message view
4. Press `b` or `Escape` to return to inbox

#### Switching Folders
1. Click on a folder in the sidebar, or
2. Use arrow keys to navigate folders and press `Enter`
3. Messages for that folder will load automatically

#### Searching
1. Press `/` to focus the search bar
2. Type your search query
3. Press `Enter` to search
4. Results appear in the message list
5. Press `/` again and clear to return to normal view

### Composing Emails

#### New Email
1. Press `n` from the inbox
2. Fill in recipient(s) in the "To" field (comma-separated for multiple)
3. Optionally add CC recipients
4. Enter subject
5. Type your message body
6. Press `Ctrl+S` to send, or `Escape` to cancel

#### Reply
1. Select a message in the inbox
2. Press `r` or click Reply
3. Recipient and subject are pre-filled
4. Original message is included below
5. Type your reply and send

#### Forward
1. Select a message
2. Press `f` or click Forward
3. Enter recipient(s)
4. Original message is included
5. Add your message and send

### Managing Messages

#### Marking as Read/Unread
- Press `u` to toggle read status
- Unread messages show a blue dot (●) indicator
- Read messages appear dimmed

#### Deleting Messages
- Press `d` to delete the selected message
- Deleted messages are moved to Trash folder
- Empty Trash from the Trash folder view

#### Viewing Attachments
- Messages with attachments show a 📎 icon
- Attachment count and size are displayed
- In full message view, attachments are listed with details

## Project Structure

```
Term-Mail/
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── .gitignore                   # Git ignore rules
│
├── config/                      # Configuration directory
│   └── accounts.json            # Stored account credentials
│
├── data/                        # Data directory
│   └── local_emails/            # Local email storage
│       ├── addresses.json        # Local address registry
│       └── *.json               # Email storage files
│
└── src/                         # Source code
    ├── __init__.py
    ├── app.py                   # Main Textual application
    │
    ├── models/                  # Data models
    │   ├── __init__.py
    │   ├── email.py             # Email message model
    │   └── folder.py            # Folder model
    │
    ├── providers/               # Email provider implementations
    │   ├── __init__.py
    │   ├── base.py              # Abstract base provider
    │   ├── imap_provider.py     # IMAP/SMTP provider
    │   ├── nylas_provider.py    # Nylas API provider
    │   └── local_provider.py    # Local email provider
    │
    ├── screens/                  # Application screens
    │   ├── __init__.py
    │   ├── inbox.py             # Main inbox screen
    │   ├── message_view.py      # Full message view screen
    │   ├── compose.py           # Compose/reply/forward screen
    │   ├── settings.py          # Settings and account management
    │   ├── create_local_email.py # Create local email screen
    │   └── configure_smtp.py   # SMTP configuration screen
    │
    ├── widgets/                 # Reusable UI widgets
    │   ├── __init__.py
    │   ├── message_list.py      # Message list widget
    │   ├── folder_list.py       # Folder navigation widget
    │   ├── search_bar.py        # Search input widget
    │   ├── status_bar.py        # Status indicator widget
    │   └── message_preview.py   # Message preview pane
    │
    └── utils/                   # Utility functions
        ├── __init__.py
        ├── html_parser.py       # HTML to text conversion
        ├── config.py            # Configuration management
        └── local_email_manager.py # Local email address management
```

## Architecture

### Design Patterns

**Provider Pattern**: Email providers implement a common interface (`EmailProvider`), allowing easy addition of new providers without changing core application code.

**Model-View-Controller**: 
- Models (`src/models/`) represent data structures
- Views (`src/screens/`, `src/widgets/`) handle UI
- Controllers (`src/app.py`) coordinate between models and views

**Observer Pattern**: Widgets communicate via messages (events), allowing loose coupling between components.

### Key Components

#### Email Providers
- **Base Provider** (`base.py`): Abstract interface defining email operations
- **IMAP Provider**: Direct IMAP/SMTP connection for any email service
- **Nylas Provider**: Unified API access via Nylas platform
- **Local Provider**: File-based email storage for local addresses

#### UI Framework
- **Textual**: Modern terminal UI framework providing widgets, layouts, and styling
- **Rich**: Rich text and beautiful formatting library
- **CSS-like Styling**: Textual's CSS system for consistent theming

#### Data Storage
- **JSON Configuration**: Human-readable account storage
- **File-based Email Storage**: Local emails stored as JSON files
- **No Database Required**: Simple, portable storage solution

### Data Flow

1. **User Action** → Screen/Widget receives input
2. **Event Handling** → Screen processes action
3. **Provider Call** → Async call to email provider
4. **Data Retrieval** → Provider fetches from email service
5. **Model Creation** → Data converted to Email/Folder models
6. **UI Update** → Widgets refresh with new data
7. **User Feedback** → Status bar shows operation result

## Troubleshooting

### Connection Issues

**Problem**: Cannot connect to email server
- **Solution**: 
  - Verify server addresses and ports are correct
  - Check your internet connection
  - Ensure firewall isn't blocking connections
  - For Gmail, use App Password instead of regular password

**Problem**: Authentication fails
- **Solution**:
  - Double-check username and password
  - For Gmail, enable 2FA and use App Password
  - Verify IMAP/SMTP is enabled in your email account settings

### Local Email Issues

**Problem**: Local emails not delivering
- **Solution**:
  - Ensure both sender and recipient are local addresses
  - Check that addresses exist in `data/local_emails/addresses.json`
  - Verify storage directory permissions

**Problem**: Cannot send to external addresses
- **Solution**:
  - Configure SMTP settings for your local address
  - Verify SMTP credentials are correct
  - Check SMTP server allows relaying from your IP

### UI Issues

**Problem**: Preview pane not updating
- **Solution**:
  - Press `p` to toggle preview pane
  - Navigate messages with arrow keys
  - Restart application if issue persists

**Problem**: Colors not displaying correctly
- **Solution**:
  - Ensure your terminal supports 256 colors
  - Try setting `TERM=xterm-256color` in your shell
  - Check terminal emulator color support

### Performance Issues

**Problem**: Slow loading of messages
- **Solution**:
  - Reduce message limit in fetch_emails calls
  - Check network connection speed
  - Consider using Nylas for better performance

## Contributing

Contributions are welcome! Please follow these guidelines:

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Style

- Follow PEP 8 Python style guide
- Use type hints where appropriate
- Add docstrings to functions and classes
- Keep functions focused and small

### Testing

- Test with multiple email providers
- Verify UI works in different terminal sizes
- Test error handling and edge cases

### Reporting Issues

When reporting bugs, please include:
- Python version
- Operating system
- Terminal emulator
- Steps to reproduce
- Error messages or logs

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Textual](https://github.com/Textualize/textual) - Terminal UI framework
- [Rich](https://github.com/Textualize/rich) - Rich text and beautiful formatting
- [Nylas](https://www.nylas.com/) - Email API platform
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - HTML parsing

## Support

For questions, issues, or contributions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review the documentation above

---

**Made with ❤️ for terminal enthusiasts**
