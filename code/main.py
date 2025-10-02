import os
import random
from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.sessions import StringSession

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")  
SESSION_STRING = os.getenv("SESSION_STRING")

# 👇 Multiple groups/channels allowed (comma-separated in .env)
TARGET_CHAT_IDS = [int(x) for x in os.getenv("TARGET_CHAT_IDS", "").split(",") if x]

# 👇 Hardcoded emoji list
EMOJIS = ["👍", "🔥", "❤️", "😂", "👏", "😎", "✨"]

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
OWNER_ID = None

# ✅ React handler
@client.on(events.NewMessage)
async def react_handler(event):
    if event.chat_id in TARGET_CHAT_IDS:  
        # pick one random emoji
        emojis = EMOJIS.copy()
        random.shuffle(emojis)
        for emoji in emojis:
            try:
                await event.message.react(emoji)
                break  # stop after first successful reaction
            except Exception as e:
                print(f"⚠️ Failed with {emoji}, trying next... ({e})")

async def init_owner():
    global OWNER_ID
    me = await client.get_me()
    OWNER_ID = me.id
    print(f"✅ Detected owner ID: {OWNER_ID}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await client.start()
    await init_owner()
    print("✅ Telegram client started and owner detected.")
    yield
    await client.disconnect()

app = FastAPI(lifespan=lifespan)

@app.get("/favicon.ico")
@app.head("/favicon.ico")
async def favicon():
    return b"", 204

@app.get("/")
@app.head("/")
async def home():
    return {"status": "running"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")
