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

TARGET_CHAT_IDS = [int(x) for x in os.getenv("TARGET_CHAT_IDS", "").split(",") if x]

EMOJIS = ["👍", "🔥", "❤️", "😂", "👏", "😎", "✨"]

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
OWNER_ID = None

@client.on(events.NewMessage)
async def react_handler(event):
    if event.chat_id in TARGET_CHAT_IDS:  
        emojis = EMOJIS.copy()
        random.shuffle(emojis)  # random order to pick a usable emoji

        for emoji in emojis:
            try:
                await client.send_reaction(event.chat_id, event.message.id, emoji)
                # ✅ reacted successfully, stop here
                break
            except Exception as e:
                # Only try next if this emoji is restricted
                print(f"⚠️ Failed with {emoji}, trying next... ({e})")
        else:
            # All emojis failed
            print("❌ Could not react to this message with any emoji.")

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
