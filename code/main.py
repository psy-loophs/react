from fastapi import FastAPI
import asyncio
from userbot import start_bot

app = FastAPI()

# Start bot in background on startup
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_bot())

# Simple heartbeat endpoint for Render
@app.get("/")
async def root():
    return {"status": "Bot is running"}
