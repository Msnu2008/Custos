import discord
from discord import app_commands
from discord.ext import commands

class EmbedSender(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="embed", description="Envía un mensaje embebido personalizado como el bot.")
    @app_commands.describe(
        titulo="Título del embed",
        descripcion="Contenido del mensaje (usa || para separar párrafos)",
        color="Color en hexadecimal (sin #, ej: FF0000)",
        canal="Canal donde se enviará el mensaje"
    )
    async def embed(
        self,
        interaction: discord.Interaction,
        titulo: str,
        descripcion: str,
        color: str,
        canal: discord.TextChannel
    ):
        await interaction.response.defer(ephemeral=True)

        try:
            color = int(color, 16)
        except ValueError:
            await interaction.followup.send("❌ El color debe ser un valor hexadecimal válido (ej: `FF5733`).", ephemeral=True)
            return

        # Reemplazar delimitador || por salto doble de línea
        descripcion_formateada = descripcion.replace("||", "\n\n")

        embed = discord.Embed(
            title=titulo,
            description=descripcion_formateada,
            color=color
        )
        embed.set_footer(text=f"Enviado por {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

        await canal.send(embed=embed)
        await interaction.followup.send(f"✅ Embed enviado correctamente en {canal.mention}.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(EmbedSender(bot))
