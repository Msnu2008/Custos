import discord
from discord.ext import commands
from discord import app_commands
import logging

logger = logging.getLogger(__name__)

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="perfil", description="Muestra información de un miembro.")
    @app_commands.default_permissions(administrator=True)
    async def perfil(self, interaction: discord.Interaction, usuario: discord.Member):
        await interaction.response.defer(ephemeral=True)
        roles = ", ".join(role.mention for role in usuario.roles[1:]) or "Sin roles"
        embed = discord.Embed(
            title=f"👤 Perfil de {usuario.display_name}",
            color=usuario.color
        )
        embed.set_thumbnail(url=usuario.avatar.url if usuario.avatar else usuario.default_avatar.url)
        embed.add_field(name="ID", value=usuario.id, inline=True)
        embed.add_field(name="Nombre", value=str(usuario), inline=True)
        embed.add_field(name="Rol más alto", value=usuario.top_role.mention, inline=True)
        embed.add_field(name="Roles", value=roles, inline=False)
        embed.add_field(name="Ingresó al servidor", value=usuario.joined_at.strftime("%d/%m/%Y %H:%M:%S"), inline=False)
        embed.set_footer(text=f"Creado el {usuario.created_at.strftime('%d/%m/%Y %H:%M:%S')}")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="serverinfo", description="Muestra estadísticas del servidor.")
    @app_commands.default_permissions(administrator=True)
    async def serverinfo(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        embed = discord.Embed(
            title=f"🌐 Información del servidor: {guild.name}",
            color=discord.Color.blurple()
        )
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.add_field(name="ID", value=guild.id, inline=True)
        embed.add_field(name="Miembros", value=guild.member_count, inline=True)
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        embed.add_field(name="Canales", value=len(guild.channels), inline=True)
        embed.add_field(name="Dueño", value=guild.owner.mention, inline=True)
        embed.set_footer(text=f"Creado el {guild.created_at.strftime('%d/%m/%Y %H:%M:%S')}")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="roleinfo", description="Muestra información de un rol.")
    @app_commands.default_permissions(administrator=True)
    async def roleinfo(self, interaction: discord.Interaction, rol: discord.Role):
        await interaction.response.defer(ephemeral=True)
        embed = discord.Embed(
            title=f"🔎 Información del rol: {rol.name}",
            color=rol.color
        )
        embed.add_field(name="ID", value=rol.id, inline=True)
        embed.add_field(name="Miembros", value=len(rol.members), inline=True)
        embed.add_field(name="Color", value=str(rol.color), inline=True)
        embed.add_field(name="Es gestionado", value=str(rol.managed), inline=True)
        embed.add_field(name="Es mencionable", value=str(rol.mentionable), inline=True)
        embed.set_footer(text=f"Creado el {rol.created_at.strftime('%d/%m/%Y %H:%M:%S')}")
        await interaction.followup.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Info(bot))
    logger.info("Cog Info cargado.")
