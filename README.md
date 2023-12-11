# Telegram-Switch Forwarder Bot

This bot is designed to forward messages and files from public telegram chats to
switch. This bot is built using Python and swibots+tdlib.

## Features

- Copy messages from one chat to another.
- Supports various message types, including text, photos, documents, animations,
  videos, and stickers.
- Provides real-time upload progress during file forwarding.

## Setup Instructions

### Prerequisites

1. **Telegram API Credentials:**
   - Obtain the `API_ID`, `API_HASH`, and `TELEGRAM_TOKEN` from the
     [Telegram API](https://my.telegram.org/auth).
   - Set the obtained values in the `.env` file.

2. **Enter Switch BOT TOKEN:** in `BOT_TOKEN` in `.env` file.

3. **Environment Setup:**
   - Make sure you have Python installed on your system (version 3.10 or
     higher).
   - Install the required Python packages using:
     ```
     pip install -r requirements.txt
     ```

### Run the Bot

1. **Run the bot:**
   - Execute the bot using the following command:
     ```
     python3 main.py
     ```
   - Running with docker
     ```
     docker-compose up --build
     ```

2. **Bot Commands:**
   - Interact with the bot on Switch using commands like `/start` and `/copy`.

3. **Copying Messages:**
   - Use the `/copy` command followed by the target chat username and message
     range to copy messages.

- **Customization:**
  - Feel free to customize the script to meet your specific requirements.

## Issues and Contributions

If you encounter any issues or have suggestions for improvement, please open an
issue on the GitHub repository.
