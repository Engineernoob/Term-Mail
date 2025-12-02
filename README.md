# Term-Mail

A terminal-based email client built with Python and Textual, supporting both Nylas API and direct IMAP/SMTP connections.

## Features

- View inbox and folders
- Read emails with HTML rendering
- Compose, reply, and forward emails
- Search functionality
- Attachment support
- Mark messages as read/unread
- Support for multiple email providers via Nylas or direct IMAP/SMTP
- **Create custom local email addresses** - Create your own email addresses and inboxes that work locally

## Installation

1. Install dependencies:
```bash
pip3 install -r requirements.txt
```

2. Set up your email account:
   - For Nylas: You'll need Nylas API credentials (client_id, client_secret)
   - For IMAP/SMTP: Configure your email provider settings

3. Run the application:
```bash
python3 main.py
```

## Configuration

Account configurations are stored in `config/accounts.json`. The application will prompt you to add accounts on first run.

### Nylas Setup

1. Sign up at https://dashboard.nylas.com
2. Create an application and get your Client ID and Client Secret
3. Add these credentials when adding a Nylas account in the app

### IMAP/SMTP Setup

You'll need:
- IMAP server address and port
- SMTP server address and port
- Email address and password (or app-specific password)

### Local Email Addresses

Create your own local email addresses that work entirely on your machine:
1. Press `c` from the inbox or go to Settings
2. Choose "Create Local Email" option
3. Enter a username (local part) and domain (default: "local")
4. Your email address will be created (e.g., `username@local`)
5. You can send emails between local addresses - they'll be delivered instantly!

**Sending to External Addresses:**
- When creating a local email address, you can optionally configure SMTP settings
- This allows your local email address to send emails to external addresses (Gmail, Outlook, etc.)
- Configure SMTP server, port, username, and password
- Example: Use Gmail's SMTP (smtp.gmail.com:587) with your Gmail credentials
- Your local address will appear as the "From" address, but emails are sent through the SMTP server
- You can also configure SMTP later from Settings → Configure SMTP

Local emails are stored in `data/local_emails/` directory.

## Usage

### Key Bindings

- `↑/↓`: Navigate messages
- `Enter`: Open selected message
- `n`: Compose new email
- `r`: Reply to current message
- `f`: Forward current message
- `u`: Mark as unread
- `d`: Delete message
- `/`: Search
- `c`: Create local email address
- `s`: Settings
- `q`: Quit

## Project Structure

- `src/app.py`: Main Textual application
- `src/screens/`: Application screens (inbox, message view, compose, settings, create local email)
- `src/widgets/`: Reusable UI widgets
- `src/providers/`: Email provider implementations (Nylas, IMAP/SMTP, Local)
- `src/models/`: Data models (Email, Folder)
- `src/utils/`: Utility functions (HTML parsing, configuration, local email management)
- `data/local_emails/`: Storage for local email addresses and messages

## License

MIT

