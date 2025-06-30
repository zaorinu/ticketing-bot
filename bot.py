import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import asyncio

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

WATCHED_COGS = {
    "ticket": "cogs.ticket",
    "transcript": "cogs.transcript"
}

class CogChangeHandler(FileSystemEventHandler):
    def __init__(self, loop):
        self.loop = loop

    def on_modified(self, event):
        # Quando um arquivo de cog mudar, recarregue a cog correspondente
        if event.is_directory:
            return

        for cog_name, cog_path in WATCHED_COGS.items():
            if cog_path.replace(".", "/") in event.src_path:
                print(f"♻️ Detected change in {cog_name} cog. Reloading...")
                asyncio.run_coroutine_threadsafe(reload_cog(cog_path), self.loop)
                break

async def reload_cog(cog_path):
    try:
        await bot.reload_extension(cog_path)
        print(f"✅ Reloaded cog {cog_path} successfully.")
    except Exception as e:
        print(f"❌ Failed to reload cog {cog_path}: {e}")

@bot.event
async def on_ready():
    await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"✅ Bot is online as {bot.user}")

@bot.event
async def setup_hook():
    for cog in WATCHED_COGS.values():
        await bot.load_extension(cog)

def start_watcher(loop):
    path = "./cogs"  # pasta onde ficam as cogs
    event_handler = CogChangeHandler(loop)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    print("👀 Started watching cogs for changes")
    return observer

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    observer = start_watcher(loop)
    try:
        bot.run(TOKEN)
    finally:
        observer.stop()
        observer.join()
