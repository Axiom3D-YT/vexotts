import uuid
import logging
import aiohttp
import base64
from gtts import gTTS
from src.utils.config import TIKTOK_TTS_URL, TIKTOK_VOICE_IDS

logger = logging.getLogger(__name__)

async def generate_tts(text: str, voice: str = "en_us_001", slow: bool = False) -> str:
    """Generates an MP3 file using TikTok or gTTS."""
    filename = f"temp_{uuid.uuid4()}.mp3"
    
    if voice in TIKTOK_VOICE_IDS:
        return await generate_tiktok_tts(text, voice, filename)
    else:
        # Fallback to gTTS for standard language codes
        return await generate_gtts(text, voice, slow, filename)

async def generate_tiktok_tts(text: str, voice: str, filename: str) -> str:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                TIKTOK_TTS_URL,
                json={"text": text, "voice": voice},
                headers={"Content-Type": "application/json"}
            ) as resp:
                if resp.status != 200:
                    error_data = await resp.text()
                    raise Exception(f"TikTok API Error ({resp.status}): {error_data}")
                
                data = await resp.json()
                if not data.get("success"):
                    raise Exception(f"TikTok API failed: {data.get('error')}")
                
                audio_base64 = data["data"]
                with open(filename, "wb") as f:
                    f.write(base64.b64decode(audio_base64))
                
                return filename
    except Exception as e:
        logger.error(f"TikTok TTS Error: {e}")
        raise e

async def generate_gtts(text: str, lang: str, slow: bool, filename: str) -> str:
    try:
        # gTTS is blocking, but we can run it in a thread if needed.
        # However, for simplicity stay with the current logic or improve it.
        import asyncio
        loop = asyncio.get_event_loop()
        def _save():
            tts = gTTS(text=text, lang=lang, slow=slow)
            tts.save(filename)
        
        await loop.run_in_executor(None, _save)
        return filename
    except Exception as e:
        logger.error(f"gTTS Error: {e}")
        raise e
