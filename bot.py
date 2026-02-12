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

from discord.ext import commands
from discord import app_commands

# Discord Setup
intents = discord.Intents.default()
intents.message_content = True  # Required for some interactions
bot = commands.Bot(command_prefix="!", intents=intents)
audio_lock = asyncio.Lock()

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

class TTSView(discord.ui.View):
    def __init__(self, message_text: str, guild_id: int, channel_id: int):
        super().__init__(timeout=60)
        self.message_text = message_text
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.voice = "en"
        self.slow = False

    @discord.ui.select(
        placeholder="Choose Voice Language",
        options=[
            discord.SelectOption(label="English", value="en", description="Default English"),
            discord.SelectOption(label="English (UK)", value="en-uk", description="British English"),
            discord.SelectOption(label="English (Australia)", value="en-au", description="Australian English"),
            discord.SelectOption(label="Italian", value="it", description="Italiano"),
            discord.SelectOption(label="French", value="fr", description="Français"),
            discord.SelectOption(label="Spanish", value="es", description="Español"),
            discord.SelectOption(label="German", value="de", description="Deutsch"),
        ]
    )
    async def select_voice(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.voice = select.values[0]
        await interaction.response.edit_message(content=f"Selected Voice: **{self.voice}** | Slow Mode: **{self.slow}**")

    @discord.ui.button(label="Slow Mode: OFF", style=discord.ButtonStyle.secondary)
    async def toggle_slow(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.slow = not self.slow
        button.label = f"Slow Mode: {'ON' if self.slow else 'OFF'}"
        button.style = discord.ButtonStyle.primary if self.slow else discord.ButtonStyle.secondary
        await interaction.response.edit_message(content=f"Selected Voice: **{self.voice}** | Slow Mode: **{self.slow}**", view=self)

    @discord.ui.button(label="Speak", style=discord.ButtonStyle.success)
    async def speak_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔊 Processing TTS...", ephemeral=True)
        
        # Prepare payload for trigger_tts logic
        # We call the logic directly since we are inside the bot
        payload = TTSRequest(
            guild_id=self.guild_id,
            channel_id=interaction.user.voice.channel.id if interaction.user.voice else self.channel_id,
            message=self.message_text,
            voice=self.voice,
            slow=self.slow
        )

        try:
            # We reuse the logic from trigger_tts
            await handle_tts_logic(payload)
            await interaction.edit_original_response(content="✅ TTS Sent!")
        except Exception as e:
            await interaction.edit_original_response(content=f"❌ Error: {e}")

class TTSRequest(BaseModel):
    guild_id: int
    channel_id: int
    message: str
    voice: str = "en"
    slow: bool = False

async def handle_tts_logic(payload: TTSRequest):
    """Refactored logic to be callable from both FastAPI and Slash Commands."""
    guild = bot.get_guild(payload.guild_id)
    if not guild:
        raise ValueError("Guild not found")
    
    channel = guild.get_channel(payload.channel_id)
    if not channel or not isinstance(channel, discord.VoiceChannel):
        raise ValueError("Voice channel not found")

    me = guild.me
    permissions = channel.permissions_for(me)
    if not permissions.connect or not permissions.speak:
        raise PermissionError("Bot lacks Connect/Speak permissions")

    voice_client = guild.voice_client
    
    try:
        if voice_client is None:
            voice_client = await channel.connect()
        elif voice_client.channel.id != channel.id:
            await voice_client.move_to(channel)
    except Exception as e:
        if guild.voice_client:
            await guild.voice_client.disconnect(force=True)
        raise e

    loop = asyncio.get_event_loop()
    filename = await loop.run_in_executor(None, generate_audio_file, payload.message, payload.voice, payload.slow)

    async with audio_lock:
        if voice_client.is_playing():
            voice_client.stop()
        
        def after_playing(error):
            if error:
                logger.error(f"FFmpeg Playback Error: {error}")
            cleanup_file(filename)

        source = FFmpegPCMAudio(filename)
        voice_client.play(source, after=after_playing)

        while voice_client.is_playing():
            await asyncio.sleep(0.5)

@app.post("/speak")
async def trigger_tts(payload: TTSRequest):
    if not bot.is_ready():
        raise HTTPException(status_code=503, detail="Discord bot not ready")
    try:
        await handle_tts_logic(payload)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@bot.tree.command(name="test", description="Test TTS with interactive options")
@app_commands.describe(text="The message you want the bot to say")
@app_commands.checks.has_permissions(administrator=True)
async def test(interaction: discord.Interaction, text: str):
    """Admin-only test command with interactive UI."""
    if not interaction.user.voice:
        await interaction.response.send_message("❌ You must be in a voice channel to use this!", ephemeral=True)
        return

    view = TTSView(text, interaction.guild_id, interaction.user.voice.channel.id)
    await interaction.response.send_message(
        content=f"TTS Test for: \"**{text}**\"\nSelect your options below:",
        view=view,
        ephemeral=True
    )

@bot.event
async def on_ready():
    logger.info(f"Bot logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")

@app.on_event("startup")
async def startup_event():
    if not TOKEN:
        logger.error("DISCORD_TOKEN not found")
        return
    asyncio.create_task(bot.start(TOKEN))

@app.on_event("shutdown")
async def shutdown_event():
    await bot.close()

