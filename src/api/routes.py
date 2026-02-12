from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import discord
import logging
from src.services.tts_service import generate_tts
from src.utils.audio import cleanup_file

logger = logging.getLogger(__name__)

router = APIRouter()

class TTSRequest(BaseModel):
    guild_id: int
    channel_id: int
    message: str
    voice: str = "en_us_001"
    slow: bool = False

# We will attach the bot to the router or app during startup
bot = None

@router.post("/speak")
async def trigger_tts(payload: TTSRequest):
    global bot
    if not bot or not bot.is_ready():
        raise HTTPException(status_code=503, detail="Discord bot not ready")

    guild = bot.get_guild(payload.guild_id)
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")
    
    channel = guild.get_channel(payload.channel_id)
    if not channel or not isinstance(channel, discord.VoiceChannel):
        raise HTTPException(status_code=404, detail="Voice channel not found")

    try:
        # Generate TTS
        filename = await generate_tts(payload.message, payload.voice, payload.slow)
        
        # Use the logic from tts_cog to play (or refactor play_audio to src/services/audio_service.py)
        # For simplicity, I'll import play_audio from tts_cog or move it to a shared place
        from src.cogs.tts_cog import play_audio
        await play_audio(guild, channel, filename)
        
        return {"status": "success", "channel": channel.name, "guild": guild.name}
    except Exception as e:
        logger.error(f"API TTS Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def set_bot(bot_instance):
    global bot
    bot = bot_instance
