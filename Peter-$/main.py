import asyncio
import logging
import os
from typing import Optional

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("bot")

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise RuntimeError("TOKEN is missing in .env")

PREFIX = (os.getenv("PREFIX") or "!").strip()
if not PREFIX or PREFIX == "<":
    PREFIX = "<"

TEST_GUILD_RAW = os.getenv("TEST_GUILD")
TEST_GUILD: Optional[int] = int(TEST_GUILD_RAW) if TEST_GUILD_RAW else None


class Bot(commands.Bot):
    async def setup_hook(self) -> None:
        # optional debug extension
        try:
            await self.load_extension("jishaku")
            log.info("Loaded extension: jishaku")
        except Exception:
            log.exception("Failed to load jishaku")

        # load cogs if folder exists
        if os.path.isdir("cogs"):
            for filename in os.listdir("cogs"):
                if filename.endswith(".py") and not filename.startswith("_"):
                    ext = f"cogs.{filename[:-3]}"
                    try:
                        await self.load_extension(ext)
                        log.info("Loaded extension: %s", ext)
                    except Exception:
                        log.exception("Failed to load extension: %s", ext)
        else:
            log.warning("No ./cogs folder found (skipping cog loading).")

        # sync slash commands
        try:
            if TEST_GUILD:
                guild_obj = discord.Object(id=TEST_GUILD)
                self.tree.copy_global_to(guild=guild_obj)
                synced = await self.tree.sync(guild=guild_obj)
                log.info("Synced %d app commands to guild %s", len(synced), TEST_GUILD)
            else:
                synced = await self.tree.sync()
                log.info("Synced %d app commands globally", len(synced))
        except Exception:
            log.exception("Failed to sync app commands")


intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

bot = Bot(command_prefix=PREFIX, intents=intents)


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game("ready"))
    log.info("Logged in as %s (id=%s) | prefix=%r", bot.user, bot.user.id, PREFIX)


# PREFIX COMMAND
@bot.command(name="ping")
async def ping_cmd(ctx: commands.Context):
    await ctx.reply("pong")


# SLASH COMMAND
@bot.tree.command(name="ping", description="Ping the bot")
async def ping_slash(interaction: discord.Interaction):
    await interaction.response.send_message("pong", ephemeral=True)


async def main():
    async with bot:
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())