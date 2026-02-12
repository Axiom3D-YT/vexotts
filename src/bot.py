import os
import discord
from discord.ext import commands
import logging

logger = logging.getLogger(__name__)

class VexoBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def setup_hook(self):
        # Load cogs
        logger.info("Loading Cogs...")
        await self.load_extension("src.cogs.tts_cog")
        
        # Sync slash commands
        logger.info("Syncing Slash Commands...")
        synced = await self.tree.sync()
        logger.info(f"Synced {len(synced)} command(s)")

    async def on_ready(self):
        logger.info(f"Bot logged in as {self.user}")

def get_bot():
    intents = discord.Intents.default()
    intents.message_content = True
    bot = VexoBot(command_prefix="!", intents=intents)
    return bot
