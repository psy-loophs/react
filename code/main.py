# code/main.py
import asyncio
from telethon import TelegramClient, events
from fastapi import FastAPI
import os

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION = os.environ.get("SESSION")  # Your .session string or file
OWNER_ID = int(os.environ.get("OWNER_ID"))
TARGET_GROUPS = [int(g) for g in os.environ.get("TARGET_GROUPS", "").split(",")]  # IDs
EMOJIS = ["🔥", "👏", "✨", "❤️", "😂", "👍", "😎"]

app = FastAPI()
client = TelegramClient(SESSION, API_ID, API_HASH)


async def react_to_message(event, emoji_list):
    for emoji in emoji_list:
        try:
            # Updated: use the client method send_reaction
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


@client.on(events.NewMessage(chats=TARGET_GROUPS))
async def handle_new_message(event):
    # Skip messages from the bot itself
    if event.sender_id == OWNER_ID:
        return

    await react_to_message(event, EMOJIS)


@app.on_event("startup")
async def startup_event():
    await client.start()
    me = await client.get_me()
    print(f"✅ Telegram client started. Logged in as {me.first_name} ({me.id})")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("code.main:app", host="0.0.0.0", port=8000, reload=True)
