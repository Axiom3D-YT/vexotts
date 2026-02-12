import os
import asyncio
import discord
from discord import FFmpegPCMAudio
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from gtts import gTTS
import uuid
import logging
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

app = FastAPI(title="VexoTTS API")

# Discord Setup
intents = discord.Intents.default()
bot = discord.Client(intents=intents)
audio_lock = asyncio.Lock()

class TTSRequest(BaseModel):
    guild_id: int
    channel_id: int
    message: str
    voice: str = "en"
    slow: bool = False

def generate_audio_file(text: str, lang: str, slow: bool) -> str:
    """Generates an MP3 file using gTTS."""
    filename = f"temp_{uuid.uuid4()}.mp3"
    try:
        tts = gTTS(text=text, lang=lang, slow=slow)
        tts.save(filename)
        return filename
    except Exception as e:
        logger.error(f"gTTS Error: {e}")
        raise e

def cleanup_file(filename: str):
    """Deletes the temporary audio file."""
    try:
        if os.path.exists(filename):
            os.remove(filename)
            logger.info(f"Cleaned up {filename}")
    except Exception as e:
        logger.error(f"Cleanup Error: {e}")

@app.post("/speak")
async def trigger_tts(payload: TTSRequest):
    if not bot.is_ready():
        raise HTTPException(status_code=503, detail="Discord bot is not ready")

    guild = bot.get_guild(payload.guild_id)
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")
    
    channel = guild.get_channel(payload.channel_id)
    if not channel or not isinstance(channel, discord.VoiceChannel):
        raise HTTPException(status_code=404, detail="Voice channel not found or invalid")

    # Permissions check
    me = guild.me
    permissions = channel.permissions_for(me)
    if not permissions.connect or not permissions.speak:
        raise HTTPException(status_code=403, detail="Bot lacks Connect/Speak permissions in this channel")

    voice_client = guild.voice_client
    
    try:
        if voice_client is None:
            voice_client = await channel.connect()
        elif voice_client.channel.id != channel.id:
            await voice_client.move_to(channel)
    except Exception as e:
        logger.error(f"Voice Connection Error: {e}")
        # Reset voice client if it's in a weird state
        if guild.voice_client:
            await guild.voice_client.disconnect(force=True)
        raise HTTPException(status_code=500, detail=f"Voice connection failure: {e}")

    try:
        loop = asyncio.get_event_loop()
        filename = await loop.run_in_executor(None, generate_audio_file, payload.message, payload.voice, payload.slow)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"TTS Generation Error: {e}")

    async with audio_lock:
        try:
            if voice_client.is_playing():
                voice_client.stop()
            
            def after_playing(error):
                if error:
                    logger.error(f"FFmpeg Playback Error: {error}")
                cleanup_file(filename)

            if not os.path.exists(filename):
                raise FileNotFoundError(f"TTS file {filename} was not created")

            source = FFmpegPCMAudio(filename)
            voice_client.play(source, after=after_playing)

            # Wait for playback to finish before releasing the lock
            while voice_client.is_playing():
                await asyncio.sleep(0.5)
        except Exception as e:
            cleanup_file(filename)
            logger.error(f"Playback trigger error: {e}")
            raise HTTPException(status_code=500, detail=f"Playback error: {e}")

    return {"status": "success", "channel": channel.name, "guild": guild.name}

@app.on_event("startup")
async def startup_event():
    if not TOKEN:
        logger.error("DISCORD_TOKEN not found in environment")
        return
    logger.info("Starting Discord bot...")
    asyncio.create_task(bot.start(TOKEN))

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down...")
    await bot.close()
