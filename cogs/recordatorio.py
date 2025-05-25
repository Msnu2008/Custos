import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
from datetime import datetime, timedelta

class Recordatorio(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="recordatorio", description="Establece un recordatorio personalizado.")
    @app_commands.describe(tiempo="En cuántos minutos quieres que te recuerde", mensaje="¿Qué debo recordarte?")
    async def recordatorio(
        self, interaction: discord.Interaction,
        tiempo: int,
        mensaje: str
    ):
        await interaction.response.send_message(
            f"⏳ Te recordaré en {tiempo} minuto(s): **{mensaje}**", ephemeral=True
        )
        
        await asyncio.sleep(tiempo * 60)
        
        try:
            await interaction.user.send(f"🔔 ¡Recordatorio!: {mensaje}")
        except discord.Forbidden:
            await interaction.followup.send(f"🔔 ¡Recordatorio para {interaction.user.mention}!: {mensaje}")

async def setup(bot):
    await bot.add_cog(Recordatorio(bot))
