import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Select

class AyudaSelect(Select):
    def __init__(self, categorias, asignacion):
        options = [
            discord.SelectOption(label=descripcion, value=nombre)
            for nombre, descripcion in categorias.items()
        ]
        super().__init__(placeholder="Selecciona una categoría...", options=options)
        self.categorias = categorias
        self.asignacion = asignacion

    async def callback(self, interaction: discord.Interaction):
        categoria = self.values[0]
        embed = discord.Embed(
            title=f"📚 Ayuda - {self.categorias[categoria]}",
            color=discord.Color.green()
        )
        comandos_en_categoria = [nombre for nombre, cat in self.asignacion.items() if cat == categoria]
        if comandos_en_categoria:
            embed.description = "\n".join(f"• `/{comando}`" for comando in sorted(comandos_en_categoria))
            embed.set_footer(text=f"{len(comandos_en_categoria)} comando(s) en esta categoría")
        else:
            embed.description = "No hay comandos disponibles en esta categoría."
        await interaction.response.send_message(embed=embed, ephemeral=True)

class AyudaView(View):
    def __init__(self, categorias, asignacion):
        super().__init__(timeout=180)
        self.add_item(AyudaSelect(categorias, asignacion))

class Ayuda(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.categorias = {
            "Información": "ℹ️ Información",
            "Moderación": "🛡️ Moderación",
            "AutoMod": "🤖 Auto Moderación",
            "Anuncios": "📢 Anuncios",
            "Tickets": "🎟️ Sistema de Tickets",
            "Reportes": "🚨 Reportes",
            "Mensajes": "💬 Mensajes",
            "Canales de Voz": "🔊 Gestión de canales de voz",
            "Diversión": "🎉 Diversión y Juegos",
            "Otros": "🗃️ Otros",
        }

        self.asignacion = {
            "create_ticket_panel": "Tickets",
            "set_support_role": "Tickets",
            "set_ticket_category": "Tickets",
            "set_anuncios": "Anuncios",
            "anunciar": "Anuncios",
            "ban": "Moderación",
            "expulsar": "Moderación",
            "sorteo": "Diversión",
            "mute": "Moderación",
            "unmute": "Moderación",
            "perfil": "Información",
            "set_desahogo": "Mensajes",
            "desahogar": "Mensajes",
            "sorteo": "Otros",
            "serverinfo": "Información",
            "roleinfo": "Información",
            "limpiar": "Moderación",
            "slowmode": "Moderación",
            "modlog": "Moderación",
            "infracciones": "Moderación",
            "report": "Reportes",
            "set_report": "Reportes",
            "advertir": "Moderación",
            "eliminar_advertencia": "Moderación",
            "8ball": "Diversión",
            "coinflip": "Diversión",
            "dado": "Diversión",
            "rps": "Diversión",
            "meme": "Diversión",
            "chiste": "Diversión",
            "insulto": "Diversión",
            "halago": "Diversión",
            "ship": "Diversión",
            "compatibilidad": "Diversión",
            "simparometro": "Diversión",
            "gayrate": "Diversión",
            "inteligenciametro": "Diversión",
            "abrazo": "Diversión",
            "beso": "Diversión",
            "golpe": "Diversión",
            "adivina": "Diversión",
            "animalfusion": "Diversión",
            "sabiduria": "Diversión",
            "dictador": "Diversión",
            "piedrapapelban": "Diversión",
            "horoscopo": "Diversión",
            "sabiasque": "Diversión",
            "vacuna": "Diversión",
            "ayuda": "Otros",
            "vc_setup": "Canales de Voz",
            "set_vc": "Canales de Voz",
            "vc_lock": "Canales de Voz",
            "vc_unlock": "Canales de Voz",
            "vc_limit": "Canales de Voz",
            "vc_rename": "Canales de Voz",
            "vc_claim": "Canales de Voz",
             "agregar_palabra": "Moderación",
             "listar_palabras": "Moderación",
              "eliminar_palabra": "Moderación",
        }

    @app_commands.command(name="ayuda", description="Muestra la lista de comandos disponibles.")
    async def ayuda(self, interaction: discord.Interaction):
        total_categorias = len(self.categorias)
        total_comandos = len(self.asignacion)

        descripcion_categorias = "\n".join(
            f"{emoji_desc}" for emoji_desc in self.categorias.values()
        )
        descripcion_categorias = "\n".join(
            f"{emoji} {desc}" for _, (emoji, desc) in
            enumerate(
                [(v.split()[0], " ".join(v.split()[1:])) for v in self.categorias.values()]
            )
        )

        embed = discord.Embed(
            title="🤖 Ayuda - Lista de Categorías",
            description=(
                f"Hay **{total_categorias}** categorías y **{total_comandos}** comandos disponibles.\n\n"
                "Selecciona una categoría en el menú desplegable para ver sus comandos.\n\n"
            ),
            color=discord.Color.blurple()
        )
        # Listar categorías con emojis y nombres ordenados
        embed.description += "\n".join(
            f"**{nombre}**: {descripcion}" for nombre, descripcion in self.categorias.items()
        )

        view = AyudaView(self.categorias, self.asignacion)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Ayuda(bot))
