import discord
from discord.ext import commands, tasks
import asyncio
import os
from dotenv import load_dotenv
from vinted_scraper import get_latest_vinted_items

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Config en mémoire : { marque: {"channel_id": int, "last_items": set()} }
config = {}

@bot.event
async def on_ready():
    print(f"{bot.user} est en ligne 🚀")
    check_vinted.start()

@bot.command()
async def set_channel(ctx, marque: str):
    """Lie une marque à ce salon"""
    config[marque.lower()] = {"channel_id": ctx.channel.id, "last_items": set()}
    await ctx.send(f"✅ Les annonces **{marque}** seront postées ici !")

@tasks.loop(minutes=2)
async def check_vinted():
    """Boucle qui check les annonces toutes les 2 minutes"""
    for marque, info in config.items():
        channel = bot.get_channel(info["channel_id"])
        try:
            new_items = await get_latest_vinted_items(marque)
        except Exception as e:
            print(f"❌ Erreur pendant le scraping de {marque} : {e}")
            continue

        for item in new_items:
            if item["link"] in info["last_items"]:
                continue  # déjà envoyé
            info["last_items"].add(item["link"])

            embed = discord.Embed(
                title=item["title"],
                url=item["link"],
                description=item["description"][:400] + "..." if len(item["description"]) > 400 else item["description"],
                color=0x2ecc71,
            )
            await channel.send(embed=embed)
        await asyncio.sleep(2)

bot.run(os.getenv("DISCORD_TOKEN"))
