import discord
from discord.ext import commands
from discord import app_commands
from supabase import create_client, Client
import os
import traceback

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

class DBOperations:
    def __init__(self):
        print("[DBOperations] Inicializando cliente Supabase...")
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("[DBOperations] Cliente Supabase creado.")

    def set_config(self, guild_id: int, key: str, value: str):
        print(f"[DBOperations] set_config llamado con guild_id={guild_id}, key={key}, value={value}")
        try:
            response = self.supabase.table("server_config").upsert({
                "guild_id": guild_id,
                key: value
            }, on_conflict="guild_id").execute()
            print(f"[DBOperations] set_config response: {response}")
        except Exception as e:
            print(f"[DBOperations] Error en set_config: {repr(e)}")
            traceback.print_exc()

    def get_config(self, guild_id: int) -> dict:
        print(f"[DBOperations] get_config llamado con guild_id={guild_id}")
        try:
            result = self.supabase.table("server_config").select("*").eq("guild_id", guild_id).single().execute()
            print(f"[DBOperations] get_config resultado: {result.data}")
            return result.data or {}
        except Exception as e:
            print(f"[DBOperations] Error en get_config: {repr(e)}")
            traceback.print_exc()
            return {}

    def save_desahogo(self, guild_id: int, user_id: int, mensaje: str):
        print(f"[DBOperations] save_desahogo llamado con guild_id={guild_id}, user_id={user_id}, mensaje={mensaje}")
        try:
            response = self.supabase.table("desahogos").insert({
                "guild_id": guild_id,
                "user_id": user_id,
                "mensaje": mensaje
            }).execute()
            print(f"[DBOperations] save_desahogo response: {response}")
        except Exception as e:
            print(f"[DBOperations] Error en save_desahogo: {repr(e)}")
            traceback.print_exc()


class Desahogo(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = DBOperations()
        print("[Desahogo Cog] Cog inicializado.")

    @app_commands.command(name="set_desahogo", description="Configura el canal donde se enviarán los desahogos.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(canal="El canal donde se enviarán los mensajes de desahogo")
    async def set_desahogo(self, interaction: discord.Interaction, canal: discord.TextChannel):
        print(f"[set_desahogo] Ejecutado por {interaction.user} en guild {interaction.guild_id}")
        await interaction.response.defer(ephemeral=True)
        try:
            self.db.set_config(interaction.guild.id, "desahogo_channel_id", str(canal.id))
            await interaction.followup.send(
                embed=discord.Embed(
                    title="✅ Canal configurado",
                    description=f"Los mensajes de desahogo se enviarán a {canal.mention}",
                    color=discord.Color.green()
                ),
                ephemeral=True
            )
            print(f"[set_desahogo] Canal configurado a {canal.id}")
        except Exception as e:
            print(f"[set_desahogo] Error: {repr(e)}")
            traceback.print_exc()
            await interaction.followup.send(
                f"Ocurrió un error al configurar el canal: {e}",
                ephemeral=True
            )

    @app_commands.command(name="desahogar", description="Envía un mensaje de desahogo (opcionalmente anónimo)")
    @app_commands.describe(mensaje="Mensaje para desahogarte", anonimo="Enviar anónimo?")
    async def desahogar(self, interaction: discord.Interaction, mensaje: str, anonimo: bool = False):
        print(f"[desahogar] Ejecutado por {interaction.user} en guild {interaction.guild_id} (anonimo={anonimo})")
        await interaction.response.defer(ephemeral=True)
        try:
            config = self.db.get_config(interaction.guild.id)
            channel_id = config.get("desahogo_channel_id")
            print(f"[desahogar] Canal obtenido: {channel_id}")
            if not channel_id:
                await interaction.followup.send(
                    "El canal de desahogo no está configurado. Usa /set_desahogo primero.",
                    ephemeral=True
                )
                print("[desahogar] Canal no configurado.")
                return

            channel = interaction.guild.get_channel(int(channel_id))
            if not channel:
                await interaction.followup.send(
                    "No pude encontrar el canal configurado. Reconfigúralo con /set_desahogo.",
                    ephemeral=True
                )
                print("[desahogar] Canal configurado no encontrado en el servidor.")
                return

            embed = discord.Embed(
                title="Nuevo Desahogo",
                description=mensaje,
                color=discord.Color.blurple()
            )
            embed.set_footer(text=f"De: {'Anónimo' if anonimo else interaction.user.display_name}")

            await channel.send(embed=embed)
            print(f"[desahogar] Mensaje enviado en canal {channel.id}")

            if not anonimo:
                self.db.save_desahogo(interaction.guild.id, interaction.user.id, mensaje)
                print("[desahogar] Desahogo guardado en DB")

            await interaction.followup.send(
                "Tu desahogo ha sido enviado correctamente.",
                ephemeral=True
            )
        except Exception as e:
            print(f"[desahogar] Error inesperado: {repr(e)}")
            traceback.print_exc()
            await interaction.followup.send(
                f"Ocurrió un error inesperado: {e}",
                ephemeral=True
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(Desahogo(bot))
    print("[setup] Cog Desahogo cargado.")
