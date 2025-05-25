import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import random
from datetime import timedelta

class SorteoView(discord.ui.View):
    def __init__(self, autor: discord.User, premio: str, ganadores: int, duracion: int):
        super().__init__(timeout=duracion)
        self.autor = autor
        self.premio = premio
        self.ganadores = ganadores
        self.participantes = set()

    @discord.ui.button(label="🎉 Participar", style=discord.ButtonStyle.primary)
    async def participar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.bot:
            return
        if interaction.user.id in self.participantes:
            await interaction.response.send_message("Ya estás participando en este sorteo.", ephemeral=True)
        else:
            self.participantes.add(interaction.user.id)
            await interaction.response.send_message("✅ ¡Estás dentro del sorteo!", ephemeral=True)

class Sorteo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def formatear_tiempo(self, segundos: int) -> str:
        delta = timedelta(seconds=segundos)
        minutos, segundos = divmod(delta.seconds, 60)
        horas, minutos = divmod(minutos, 60)

        partes = []
        if delta.days > 0:
            partes.append(f"{delta.days} días")
        if horas > 0:
            partes.append(f"{horas} horas")
        if minutos > 0:
            partes.append(f"{minutos} minutos")
        if segundos > 0:
            partes.append(f"{segundos} segundos")

        return ", ".join(partes)

    @app_commands.command(name="sorteo", description="Inicia un sorteo con botón de participación")
    @app_commands.describe(duracion="Duración del sorteo en segundos", ganadores="Cantidad de ganadores", premio="Premio del sorteo")
    async def sorteo(self, interaction: discord.Interaction, duracion: int, ganadores: int, premio: str):
        await interaction.response.defer()

        tiempo_legible = self.formatear_tiempo(duracion)
        view = SorteoView(interaction.user, premio, ganadores, duracion)

        embed = discord.Embed(
            title="🎉 ¡Nuevo Sorteo!",
            description=f"**🎁 Premio:** {premio}\n"
                        f"👥 **Ganadores:** {ganadores}\n"
                        f"⏳ **Termina en:** {tiempo_legible}",
            color=discord.Color.blurple()
        )
        embed.set_footer(text=f"Iniciado por {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

        mensaje = await interaction.channel.send(embed=embed, view=view)
        await interaction.followup.send("✅ Sorteo iniciado correctamente.", ephemeral=True)

        async def finalizar_sorteo():
            await view.wait()

            participantes_ids = list(view.participantes)
            if len(participantes_ids) < ganadores:
                await interaction.channel.send("❌ No hubo suficientes participantes para elegir ganadores.")
                return

            ganadores_ids = random.sample(participantes_ids, ganadores)
            menciones = ", ".join([f"<@{uid}>" for uid in ganadores_ids])

            mensaje_final = (
                f"🎉 **¡Sorteo finalizado!** 🎉\n"
                f"🏆{menciones} {'Ganó' if ganadores == 1 else 'Ganaron'} **{premio}** sorteado por {interaction.user.mention}\n"
            )
            await interaction.channel.send(mensaje_final)

            embed_final = discord.Embed(
                title="🎊 Sorteo Finalizado",
                description=f"{'Ganador' if ganadores == 1 else 'Ganadores'}: {menciones}\n🎁 Premio: {premio}",
                color=discord.Color.green()
            )
            await interaction.channel.send(embed=embed_final)

        asyncio.create_task(finalizar_sorteo())

async def setup(bot):
    await bot.add_cog(Sorteo(bot))
