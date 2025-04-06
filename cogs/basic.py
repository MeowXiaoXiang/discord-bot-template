import discord
from discord.ext import commands

from loguru import logger

class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 前綴指令範例
    @commands.command(name="ping")
    async def ping(self, ctx):
        """Ping Pong"""
        logger.info("收到 ping 指令 (前綴指令)")
        await ctx.send("Pong!")

    # 斜線指令範例
    @discord.app_commands.command(name="ping_slash")
    async def ping_slash(self, interaction: discord.Interaction):
        """Ping Pong (斜線指令)"""
        logger.info("收到 ping_slash 指令 (斜線指令)")
        await interaction.response.send_message("Pong!")

    # 混合指令範例
    @commands.hybrid_command(name="ping_hybrid")
    async def ping_hybrid(self, ctx):
        """Ping Pong (混合指令)"""
        logger.info("收到 ping_hybrid 指令 (混合指令)")
        await ctx.send("Pong!")

async def setup(bot):
    await bot.add_cog(Basic(bot))