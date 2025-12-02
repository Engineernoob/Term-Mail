#!/usr/bin/env python3
"""Term-Mail - Terminal Email Client Entry Point"""

import asyncio
from src.app import TermMailApp


def main():
    """Main entry point"""
    app = TermMailApp()
    app.run()


if __name__ == "__main__":
    main()

