from fastapi import FastAPI
import asyncio
from userbot import start_bot  # your bot logic async function

app = FastAPI()

# Start bot in background (non-blocking)
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_bot())

# Heartbeat endpoint — Render sees this immediately
@app.get("/")
async def root():
    return {"status": "Bot running"}
