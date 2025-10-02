# code/main.py
import asyncio
from fastapi import FastAPI
from telethon import TelegramClient, events
from telethon.sessions import StringSession
import os
import sys
from dotenv import load_dotenv

# -------------------------------
# Load .env automatically
# -------------------------------
load_dotenv()

# -------------------------------
# Helper to read environment variables
# -------------------------------
def get_env_var(name, required=True):
    value = os.environ.get(name)
    if value is None:
        if required:
            print(f"❌ ERROR: Environment variable {name} is not set.")
            sys.exit(1)
        return None
    return value

# -------------------------------
# Environment Variables
# -------------------------------
API_ID = int(get_env_var("API_ID"))
API_HASH = get_env_var("API_HASH")
SESSION_STRING = get_env_var("SESSION_STRING")  # String session
TARGET_CHAT_IDS = [
    int(g) for g in get_env_var("TARGET_CHAT_IDS", required=False).split(",") if g
]

# Default emoji list
EMOJIS = ["🔥", "👏", "✨", "❤️", "😂", "👍", "😎"]

# -------------------------------
# FastAPI and Telethon Client
# -------------------------------
app = FastAPI()
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

OWNER_ID = None  # Will be detected automatically

# -------------------------------
# Reaction function
# -------------------------------
async def react_to_message(event, emoji_list):
    for emoji in emoji_list:
        try:
            await client.send_reaction(
                entity=event.chat_id,
                message=event.message.id,
                reaction=emoji
            )
            print(f"✅ Reacted with {emoji}")
            return True
        except Exception as e:
            print(f"⚠️ Failed with {emoji}, trying next... {e}")
    print("❌ Could not react to this message with any emoji.")
    return False

# -------------------------------
# Handle new messages
# -------------------------------
@client.on(events.NewMessage(chats=TARGET_CHAT_IDS))
async def handle_new_message(event):
    if event.sender_id == OWNER_ID:
        return
    await react_to_message(event, EMOJIS)

# -------------------------------
# FastAPI startup event
# -------------------------------
@app.on_event("startup")
async def startup_event():
    global OWNER_ID
    await client.start()
    me = await client.get_me()
    OWNER_ID = me.id
    print(f"✅ Telegram client started. Logged in as {me.first_name} ({OWNER_ID})")

# -------------------------------
# Run with python code/main.py
# -------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
