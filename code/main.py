import os
import random
from dotenv import load_dotenv
from telethon import TelegramClient, events, functions, types
from telethon.sessions import StringSession

# Load .env variables
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
TARGET_CHAT_IDS = [int(x) for x in os.getenv("TARGET_CHAT_IDS").split(",")]
BIG_REACTION = os.getenv("BIG_REACTION", "False").lower() == "true"
ADD_TO_RECENT = os.getenv("ADD_TO_RECENT", "True").lower() == "true"

# Emoji list (keep in code)
REACTION_EMOJIS = [
    "👍", "❤️", "😂", "😮", "😢", "😡", "😱", "👏", "🔥", "🎉",
    "😎", "🐳", "👾", "💯", "🤯", "💖", "💥", "🥳", "😏", "😍",
    "🙏", "💩", "💫"
]

# Initialize client
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

if __name__ == "__main__":
    client.start()
    print("🚀 Userbot running... reacting randomly in target groups.")
    client.run_until_disconnected()
