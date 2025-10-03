import os
import random
import asyncio
import logging
from dotenv import load_dotenv
from telethon import TelegramClient, events, functions, types
from telethon.sessions import StringSession
from telethon.errors import RPCError

# ===== Load environment variables =====
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
TARGET_CHAT_IDS = [int(x) for x in os.getenv("TARGET_CHAT_IDS").split(",")]
BIG_REACTION = os.getenv("BIG_REACTION", "False").lower() == "true"
ADD_TO_RECENT = os.getenv("ADD_TO_RECENT", "True").lower() == "true"

# ===== Emoji list =====
REACTION_EMOJIS = [
    "👍", "❤️", "😂", "😮", "😢", "😡", "😱", "👏", "🔥", "🎉",
    "😎", "🐳", "👾", "💯", "🤯", "💖", "💥", "🥳", "😏", "😍",
    "🙏", "💩", "💫"
]

# ===== Logging =====
logging.basicConfig(
    filename="userbot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ===== Initialize Telegram client =====
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# ===== React to messages =====
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
            logging.info(f"✅ Reacted with {emoji} to message {event.id} in chat {event.chat_id}")
            break
        except RPCError as e:
            logging.warning(f"⚠️ Emoji {emoji} failed in chat {event.chat_id}: {e}")
        except Exception as e:
            logging.error(f"❌ Unexpected error for message {event.id} in chat {event.chat_id}: {e}")
    else:
        logging.error(f"❌ No valid emoji could be used in chat {event.chat_id} for message {event.id}")

# ===== Function to start the bot =====
async def start_bot():
    while True:
        try:
            await client.start()
            logging.info("🚀 Userbot started...")
            await client.run_until_disconnected()
        except Exception as e:
            logging.error(f"⚠️ Connection lost. Reconnecting in 5s... {e}")
            await asyncio.sleep(5)
