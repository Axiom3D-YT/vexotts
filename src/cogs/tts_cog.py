import discord
from discord import app_commands, FFmpegPCMAudio
from discord.ext import commands
import asyncio
import math
import logging
from src.utils.config import ALL_VOICES
from src.services.tts_service import generate_tts
from src.utils.audio import cleanup_file

logger = logging.getLogger(__name__)

class VoicePickerView(discord.ui.View):
    def __init__(self, message_text: str, guild_id: int, channel_id: int, page: int = 0):
        super().__init__(timeout=180)
        self.message_text = message_text
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.page = page
        self.per_page = 25
        self.selected_voice = "en_us_001"
        self.slow = False
        self._render()

    @property
    def total_pages(self):
        return math.ceil(len(ALL_VOICES) / self.per_page)

    def _get_page_items(self):
        start = self.page * self.per_page
        end = start + self.per_page
        return ALL_VOICES[start:end]

    def _render(self):
        self.clear_items()
        
        # Voice Dropdown
        items = self._get_page_items()
        options = [
            discord.SelectOption(label=name, value=vid, default=(vid == self.selected_voice))
            for vid, name in items
        ]
        
        select = discord.ui.Select(
            placeholder=f"Select Voice (Page {self.page + 1}/{self.total_pages})",
            options=options
        )
        select.callback = self.select_callback
        self.add_item(select)

        # Pagination Buttons
        prev_btn = discord.ui.Button(label="⬅️ Previous", disabled=(self.page == 0))
        prev_btn.callback = self.prev_page
        self.add_item(prev_btn)

        next_btn = discord.ui.Button(label="Next ➡️", disabled=(self.page >= self.total_pages - 1))
        next_btn.callback = self.next_page
        self.add_item(next_btn)

        # Slow Toggle
        slow_btn = discord.ui.Button(
            label=f"Slow Mode: {'ON' if self.slow else 'OFF'}",
            style=(discord.ButtonStyle.primary if self.slow else discord.ButtonStyle.secondary)
        )
        slow_btn.callback = self.toggle_slow
        self.add_item(slow_btn)

        # Speak Button
        speak_btn = discord.ui.Button(label="🔊 Speak", style=discord.ButtonStyle.success)
        speak_btn.callback = self.speak_callback
        self.add_item(speak_btn)

    async def select_callback(self, interaction: discord.Interaction):
        self.selected_voice = interaction.data["values"][0]
        await interaction.response.edit_message(content=self._get_content(), view=self)

    async def prev_page(self, interaction: discord.Interaction):
        self.page -= 1
        self._render()
        await interaction.response.edit_message(content=self._get_content(), view=self)

    async def next_page(self, interaction: discord.Interaction):
        self.page += 1
        self._render()
        await interaction.response.edit_message(content=self._get_content(), view=self)

    async def toggle_slow(self, interaction: discord.Interaction):
        self.slow = not self.slow
        self._render()
        await interaction.response.edit_message(content=self._get_content(), view=self)

    def _get_content(self):
        return (f"TTS Test: \"**{self.message_text}**\"\n"
                f"Selected: **{self.selected_voice}** | Slow: **{self.slow}**")

    async def speak_callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("🔊 Processing...", ephemeral=True)
        
        guild = interaction.guild
        channel = interaction.user.voice.channel if interaction.user.voice else None
        
        if not channel:
            await interaction.edit_original_response(content="❌ Join a voice channel first!")
            return

        try:
            filename = await generate_tts(self.message_text, self.selected_voice, self.slow)
            await play_audio(guild, channel, filename)
            await interaction.edit_original_response(content="✅ TTS Sent!")
        except Exception as e:
            await interaction.edit_original_response(content=f"❌ Error: {e}")

async def play_audio(guild: discord.Guild, channel: discord.VoiceChannel, filename: str):
    """Internal helper to speak in a channel."""
    voice_client = guild.voice_client
    
    if voice_client is None:
        voice_client = await channel.connect()
    elif voice_client.channel.id != channel.id:
        await voice_client.move_to(channel)

    if voice_client.is_playing():
        voice_client.stop()

    def after_playing(error):
        if error:
            logger.error(f"Playback Error: {error}")
        cleanup_file(filename)

    source = FFmpegPCMAudio(filename)
    voice_client.play(source, after=after_playing)

class TTSCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="test", description="Test TTS with all available voices")
    @app_commands.checks.has_permissions(administrator=True)
    async def test(self, interaction: discord.Interaction, text: str):
        if not interaction.user.voice:
            await interaction.response.send_message("❌ You must be in a voice channel!", ephemeral=True)
            return

        view = VoicePickerView(text, interaction.guild_id, interaction.user.voice.channel.id)
        await interaction.response.send_message(
            content=view._get_content(),
            view=view,
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(TTSCog(bot))
