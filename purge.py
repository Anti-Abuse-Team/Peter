import discord
from discord.ext import commands

from utils.variables import admin


class Purge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="purge",
        description="Purge messages from a specific user."
    )
    @discord.app_commands.describe(
        user="The user whose messages you want to delete",
        amount="Number of messages to scan"
    )
    async def purge(
        self,
        ctx: commands.Context,
        user: discord.User,
        amount: int
    ):
        # Permission check — only admin roles can use this
        if not any(r.id in admin for r in ctx.author.roles):
            embed = discord.Embed(
                title="<:Cross:1492630473845772548> No Permission",
                description="You do not have permission to execute this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        if amount < 1:
            embed = discord.Embed(
                title="<:Cross:1492630473845772548> Invalid Amount",
                description="Amount must be at least 1.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        # Defer since this might take a bit
        await ctx.defer(ephemeral=True)

        # Track stats
        deleted_count = 0
        total_scanned = 0

        # Use purge with a check lambda
        def check(msg: discord.Message) -> bool:
            nonlocal total_scanned
            total_scanned += 1
            return msg.author.id == user.id

        try:
            deleted = await ctx.channel.purge(
                limit=amount,
                check=check,
                before=ctx.message.created_at,
                bulk=True,
                reason=f"Purge by {ctx.author} (target: {user})"
            )
            deleted_count = len(deleted)
        except discord.Forbidden:
            embed = discord.Embed(
                title="<:Cross:1492630473845772548> Missing Permissions",
                description="I don't have permission to delete messages in this channel.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        except discord.HTTPException as e:
            embed = discord.Embed(
                title="<:Cross:1492630473845772548> Error",
                description=f"Failed to purge messages: {e}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        # Build result embed
        desc_parts = [
            f"**Target User:** {user.mention} (`{user.id}`)",
            f"**Deleted:** {deleted_count} message{'s' if deleted_count != 1 else ''}",
            f"**Scanned:** {total_scanned} message{'s' if total_scanned != 1 else ''}"
        ]

        embed = discord.Embed(
            title="<:Check:1492629423600570508> Purge Complete",
            description="\n".join(desc_parts),
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Executed by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed, ephemeral=True)

        # Also log to a purge log channel if it exists
        log_channel_id = 1492638575928414279  # same log channel used by crashes
        log_channel = ctx.guild.get_channel(log_channel_id)
        if log_channel:
            log_embed = discord.Embed(
                title="<:Alert:1492637717798981702> Purge Executed",
                description=(
                    f"**Executor:** {ctx.author} (`{ctx.author.id}`)\n"
                    f"**Channel:** {ctx.channel.mention}\n"
                    f"**Target:** {user} (`{user.id}`)\n"
                    f"**Deleted:** {deleted_count}\n"
                    f"**Scanned:** {total_scanned}"
                ),
                color=0xF9A825
            )
            await log_channel.send(embed=log_embed)


async def setup(bot):
    await bot.add_cog(Purge(bot))