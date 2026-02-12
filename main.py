import os
import asyncio
import logging
import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv
from src.bot import get_bot
from src.api.routes import router, set_bot

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Initialize FastAPI
app = FastAPI(title="VexoTTS API")
app.include_router(router)

@app.on_event("startup")
async def startup_event():
    if not TOKEN:
        logger.error("DISCORD_TOKEN not found in environment!")
        return

    # Initialize Bot
    bot = get_bot()
    set_bot(bot)
    
    # Start bot in a task
    asyncio.create_task(bot.start(TOKEN))
    logger.info("Discord bot starting...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down...")

if __name__ == "__main__":
    # Run uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4200)
