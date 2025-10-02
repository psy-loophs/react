# code/main.py
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from fastapi import FastAPI
import os
import sys
from dotenv import load_dotenv

# Load .env automatically
load_dotenv()

# Helper to read env variables safely
def get_env_var(name, required=True):
    value = os.environ.get(name)
    if value is None:
        if required:
            print(f"❌ ERROR: Environment variable {name} is not set.")
            sys.exit(1)
        return None
    return value

# Load environment variables
API_ID = int(get_env_var("API_ID"))
API_HASH = get_env_var("API_HASH")
SESSION_STRING = get_env_var("SESSION_STRING")  # string session
TARGET_CHAT_IDS = [int(g) for g in get_env_var("TARGET_CHAT_IDS", required=False).split(",") if g]

EMOJIS = ["🔥", "👏", "✨", "❤️", "😂", "👍", "😎"]

# FastAPI and Telethon client
app = FastAPI()
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

OWNER_ID = None  # will detect automatically on startup


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


@client.on(events.NewMessage(chats=TARGET_CHAT_IDS))
async def handle_new_message(event):
    if event.sender_id == OWNER_ID:
        return
    await react_to_message(event, EMOJIS)


@app.on_event("startup")
async def startup_event():
    global OWNER_ID
    await client.start()
    me = await client.get_me()
    OWNER_ID = me.id
    print(f"✅ Telegram client started. Logged in as {me.first_name} ({OWNER_ID})")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("code.main:app", host="0.0.0.0", port=8000, reload=True)
