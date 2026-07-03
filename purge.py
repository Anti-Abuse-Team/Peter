import discord
from discord.ext import commands
from datetime import datetime, timedelta, timezone

from utils.variables import purge_roles


class Purge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="purge",
        description="Purge messages from a specific user. Respects Discord's 14-day bulk delete limit."
    )
    @discord.app_commands.describe(
        user="The user whose messages you want to delete",
        amount="Number of messages to scan (will only delete those within the age limit)",
        max_age_hours="Max age of messages to delete in hours (default: 336 = 14 days, Discord's limit)"
    )
    async def purge(
        self,
        ctx: commands.Context,
        user: discord.User,
        amount: int,
        max_age_hours: int = 336
    ):
        # Permission check — only specific role IDs can use this
        if not any(r.id in purge_roles for r in ctx.author.roles):
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

        if max_age_hours < 1:
            embed = discord.Embed(
                title="<:Cross:1492630473845772548> Invalid Max Age",
                description="Max age must be at least 1 hour.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        # Enforce Discord's 14-day (336 hour) limit — warn if user set higher
        discord_limit_hours = 336
        effective_max_age = min(max_age_hours, discord_limit_hours)
        cut_off = datetime.now(timezone.utc) - timedelta(hours=effective_max_age)

        # Defer since this might take a bit
        await ctx.defer(ephemeral=True)

        # Track stats
        deleted_count = 0
        skipped_old = 0
        total_scanned = 0

        # Use purge with a check lambda
        def check(msg: discord.Message) -> bool:
            nonlocal total_scanned, skipped_old
            total_scanned += 1
            if msg.author.id != user.id:
                return False
            if msg.created_at < cut_off:
                skipped_old += 1
                return False
            return True

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
        if skipped_old > 0:
            desc_parts.append(
                f"**Skipped (older than {effective_max_age}h):** {skipped_old} message{'s' if skipped_old != 1 else ''}"
            )
        if effective_max_age < max_age_hours:
            desc_parts.append(
                f"\n*Max age capped at {discord_limit_hours}h (Discord's limit).*"
            )

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
                    f"**Scanned:** {total_scanned}\n"
                    f"**Max Age:** {effective_max_age}h\n"
                    f"**Skipped (old):** {skipped_old}"
                ),
                color=0xF9A825
            )
            await log_channel.send(embed=log_embed)

    @purge.error
    async def purge_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="<:Cross:1492630473845772548> Missing Arguments",
                description="Usage: `!purge <user> <amount> [max_age_hours]` or `/purge user: amount: max_age_hours:`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Purge(bot))