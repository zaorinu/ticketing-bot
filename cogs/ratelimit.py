import discord
from discord.ext import commands
import time

class RateLimitCog(commands.Cog):
    def __init__(self, bot, cooldown=5):
        self.bot = bot
        self.cooldown = cooldown
        self._last_used = {}

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type not in (discord.InteractionType.application_command, discord.InteractionType.component):
            return

        user_id = interaction.user.id
        now = time.monotonic()

        last = self._last_used.get(user_id, 0)
        if now - last < self.cooldown:
            # Silently block without responding twice
            return

        self._last_used[user_id] = now

async def setup(bot):
    await bot.add_cog(RateLimitCog(bot))
