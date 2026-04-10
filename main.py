import asyncio
import os

import discord
from discord.ext import commands
from colorama import Fore
from dotenv import load_dotenv
import jishaku


# Explicitly load .env from project root (CWD) to avoid path ambiguity
ENV_PATH = os.path.join(os.getcwd(), ".env")
load_dotenv(dotenv_path=ENV_PATH, override=True)

TOKEN = (os.getenv("TOKEN") or "").strip()
PREFIX = os.getenv("PREFIX", "!")

if not TOKEN:
    raise RuntimeError(
        "Missing TOKEN environment variable. Add TOKEN=your_discord_bot_token to your .env file."
    )

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix=PREFIX, intents=intents)


@client.event
async def on_ready():
    await client.load_extension("jishaku")
    await client.change_presence(activity=discord.Game("[FREE ADMIN]"))
    print(f"Logged in as {client.user}")
    synced = await client.tree.sync()
    print(f"Synced {len(synced)} commands globally.")

async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await client.load_extension(f"cogs.{filename[:-3]}")
                print(f"{Fore.GREEN}[+]{Fore.RESET} Loaded {filename[:-3]}")
            except Exception as E:
                print(f"{Fore.RED}[-]{Fore.RESET} Failed to load {filename[:-3]} ({E})")

async def main():
    async with client:
        await load_cogs()
        await client.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
