import os
import asyncio
from discord.ext import commands
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv
import discord

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

class CogChangeHandler(FileSystemEventHandler):
    def __init__(self, loop, bot):
        self.loop = loop
        self.bot = bot

    def on_modified(self, event):
        if event.is_directory:
            return

        if not event.src_path.endswith(".py"):
            return

        rel_path = os.path.relpath(event.src_path).replace("\\", "/")
        if not rel_path.startswith("cogs/"):
            return

        cog_path = rel_path[:-3].replace("/", ".")

        print(f"♻️ Detected change in cog {cog_path}. Reloading...")

        asyncio.run_coroutine_threadsafe(self.reload_cog(cog_path), self.loop)

    async def reload_cog(self, cog_path):
        try:
            await self.bot.reload_extension(cog_path)
            print(f"✅ Reloaded cog {cog_path} successfully.")
        except Exception as e:
            print(f"❌ Failed to reload cog {cog_path}: {e}")

def start_watcher(loop, bot):
    path = "./cogs"
    event_handler = CogChangeHandler(loop, bot)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    print("👀 Started watching cogs for changes")
    return observer

@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user}")

@bot.event
async def setup_hook():
    # Load all cogs on startup
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            cog_name = f"cogs.{filename[:-3]}"
            try:
                await bot.load_extension(cog_name)
                print(f"✅ Loaded cog {cog_name}")
            except Exception as e:
                print(f"❌ Failed to load cog {cog_name}: {e}")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    observer = start_watcher(loop, bot)
    try:
        bot.run(TOKEN)
    finally:
        observer.stop()
        observer.join()
