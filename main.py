import asyncio
import os

import discord
from discord.ext import commands
from colorama import Fore
from dotenv import load_dotenv
import jishaku

from views.ReactionRoles.ReactionRoles import PingReactionRoles, ColorReactionRoles, LeaveReactionRoles


load_dotenv()
intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix=os.getenv("PREFIX"), intents=intents)


@client.event
async def on_ready():
    await client.load_extension("jishaku")
    await client.change_presence(activity=discord.Game("[FREE ADMIN]"))

    print(f"{Fore.YELLOW}[!]{Fore.RESET} Logged in as {client.user}")
    synced = await client.tree.sync()
    print(f"{Fore.YELLOW}[!]{Fore.RESET} Synced {len(synced)} commands globally.")

    channel = client.get_channel(1264271300977758328)

    ping_roles = await channel.fetch_message(1492586341127421982)
    color_roles = await channel.fetch_message(1492586343929221272)
    leave_roles = await channel.fetch_message(1492586343052873950)
    await ping_roles.edit(view=PingReactionRoles())
    print(f"{Fore.YELLOW}[!]{Fore.RESET} Loaded ping reaction roles.")
    await color_roles.edit(view=ColorReactionRoles())
    print(f"{Fore.YELLOW}[!]{Fore.RESET} Loaded color reaction roles.")
    await leave_roles.edit(view=LeaveReactionRoles())
    print(f"{Fore.YELLOW}[!]{Fore.RESET} Loaded leave reaction roles.")

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
        await client.start(os.getenv("TOKEN"))


if __name__ == "__main__":
    asyncio.run(main())