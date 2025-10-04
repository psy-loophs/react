import random
import os
import sys
import asyncio
import threading
from telethon import TelegramClient, events, functions, types
from telethon.sessions import StringSession
from fastapi import FastAPI
import uvicorn
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
TARGET_CHAT_IDS = [
    int(chat_id.strip()) for chat_id in os.getenv("TARGET_CHAT_IDS", "").split(",") if chat_id.strip()
]

REACTION_EMOJIS = ["👍", "👎", "❤", "🔥", "🥰", "👏", "😁", "🤔", "🤯", "😱", "🤬", "😢", "🎉", "🤩", "🤮", "💩", "🙏", "👌", "🕊", "🤡", "🥱", "🥴", "😍", "🐳", "❤️‍🔥", "🌚", "🌭", "💯", "🤣", "⚡", "🍌", "🏆", "💔", "🤨", "😐", "🍓", "🍾", "💋", "🖕", "😈", "😴", "😭", "🤓", "👻", "👨‍💻", "👀", "🎃", "🙈", "😇", "😨", "🤝", "✍", "🤗", "🫡", "🎅", "🎄", "☃", "💅", "🤪", "🗿", "🆒", "💘", "🙉", "🦄", "😘", "💊", "🙊", "😎", "👾", "🤷‍♂️", "🤷", "🤷‍♀️", "😡"]
BIG_REACTION = False
ADD_TO_RECENT = True

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

@client.on(events.NewMessage(chats=TARGET_CHAT_IDS))
async def react_to_messages(event):
    emojis = REACTION_EMOJIS.copy()
    random.shuffle(emojis)

    for emoji in emojis:
        try:
            await client(functions.messages.SendReactionRequest(
                peer=event.chat_id,
                msg_id=event.id,
                reaction=[types.ReactionEmoji(emoticon=emoji)],
                big=BIG_REACTION,
                add_to_recent=ADD_TO_RECENT
            ))
            print(f"✅ Reacted with {emoji} to message {event.id} in chat {event.chat_id}")
            break
        except Exception as e:
            print(f"⚠️ Emoji {emoji} failed in chat {event.chat_id}: {e}")
    else:
        print(f"❌ No valid emoji could be used in chat {event.chat_id} for message {event.id}")

async def init_owner():
    await client.connect()
    if not await client.is_user_authorized():
        print("❌ Session is invalid or expired. Make sure SESSION_STRING is correct.")
        sys.exit(1)

    me = await client.get_me()
    if me is None:
        print("❌ Could not retrieve account info. SESSION_STRING may be invalid.")
        sys.exit(1)
    print(f"👑 Owner ID detected: {me.id}")

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "ok", "message": "Userbot is alive"}

def run_health_server():
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

async def main():
    await init_owner()
    print("🚀 Userbot is running...")
    threading.Thread(target=run_health_server, daemon=True).start()
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
