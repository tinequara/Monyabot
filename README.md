
# Telegram Bot with integration AI

This is a **Telegram bot** that interacts with users in group chats. It listens for specific mentions (e.g., "Моня") and responds using AI. The bot is informal, sarcastic, and humorous.
## Important: 
- The **API** calls in the code are implemented for simplicity, not security. They are not intended for production environments and should not be used in sensitive or high-security applications.
## Note:
- The bot works ONLY in group chats.

## Features

- **Commands:**
  - `/start` - Turn on
  - `/stop` - Turn off
  - `/info` - Info about bot

- **Message Handling:**
  - Responds when mentioned or if someone replies to its messages.
  - Ensures response within 30 seconds of receiving a message.

- **NeuroAPI Integration:**
  - Uses **NeuroAPI** to generate responses in a sarcastic and funny tone.

- **Chat Monitoring:**
  - The bot checks if the chat is open before replying.

## Setup

1. Clone repo:
   ```bash
   git clone https://github.com/tinequara/monyabot.git

2. Install required:
   ```bash
   pip install -r requirements.txt
   
4. **Change tokens in code** (view Important)
   ```bash
   TELEGRAM_TOKEN = "your"
   NEUROAPI_KEY = "your"
3. Run the bot:
   ```bash
   py monya_bot.py
