import discord
from discord.ext import commands
from datetime import datetime
import pytz

from utils.databases import roles_db

class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_timestamp(self):
        """Get current timestamp in EST"""
        tz = pytz.timezone("US/Eastern")
        return datetime.now(tz).strftime("%m/%d/%y %I:%M %p")

    def log_to_db(self, user_id: int, role_id: int, role_name: str, action: str, mod_id: int):
        """Log a role action to MongoDB with timestamp, role name, and role ID"""
        timestamp = self.get_timestamp()
        roles_db.insert_one({
            "user_id": user_id,
            "role_id": role_id,
            "role_name": role_name,
            "action": action,
            "moderator_id": mod_id,
            "timestamp": timestamp,
            "full_date": datetime.now(pytz.timezone("US/Eastern")).isoformat()
        })

    @commands.hybrid_group()
    async def role(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid command. Use `/role add`, `/role remove`, or `/rolepersist remove`.")

    @role.command(name="add", description="Add a role to a user")
    async def add(self, ctx: commands.Context, user: discord.Member, role: discord.Role):
        """Add a role to a user and log it to the database"""
        if role in user.roles:
            return await ctx.send(f"❌ {user.mention} already has the {role.mention} role.", ephemeral=True)

        try:
            await user.add_roles(role, reason=f"Role added by {ctx.author} ({ctx.author.id})")
            self.log_to_db(user.id, role.id, role.name, "add", ctx.author.id)

            embed = discord.Embed(
                title="✅ Role Added",
                description=f"**User:** {user.mention} (`{user.id}`)\n**Role:** {role.mention} (`{role.name}` | `{role.id}`)\n**Added by:** {ctx.author.mention}\n**Time:** {self.get_timestamp()}",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to add that role. Make sure my role is higher than the target role.", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {e}", ephemeral=True)

    @role.command(name="remove", description="Remove a role from a user")
    async def remove(self, ctx: commands.Context, user: discord.Member, role: discord.Role):
        """Remove a role from a user and log it to the database"""
        if role not in user.roles:
            return await ctx.send(f"❌ {user.mention} doesn't have the {role.mention} role.", ephemeral=True)

        try:
            await user.remove_roles(role, reason=f"Role removed by {ctx.author} ({ctx.author.id})")
            self.log_to_db(user.id, role.id, role.name, "remove", ctx.author.id)

            embed = discord.Embed(
                title="✅ Role Removed",
                description=f"**User:** {user.mention} (`{user.id}`)\n**Role:** {role.mention} (`{role.name}` | `{role.id}`)\n**Removed by:** {ctx.author.mention}\n**Time:** {self.get_timestamp()}",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to remove that role. Make sure my role is higher than the target role.", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {e}", ephemeral=True)

    @commands.hybrid_group()
    async def rolepersist(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid command. Use `/rolepersist remove`.")

    @rolepersist.command(name="remove", description="Remove a persisted role from a user")
    async def persist_remove(self, ctx: commands.Context, user: discord.Member, role: discord.Role):
        """Remove a role from a user and remove it from persisted roles in the database"""
        try:
            if role in user.roles:
                await user.remove_roles(role, reason=f"Persisted role removed by {ctx.author} ({ctx.author.id})")

            # Remove from persisted roles in database
            from utils.databases import roles_db as sync_roles_db
            sync_roles_db.update_one(
                {"user_id": user.id},
                {"$pull": {"persisted_roles": role.id}}
            )

            self.log_to_db(user.id, role.id, role.name, "persist_remove", ctx.author.id)

            embed = discord.Embed(
                title="✅ Persisted Role Removed",
                description=f"**User:** {user.mention} (`{user.id}`)\n**Role:** {role.mention} (`{role.name}` | `{role.id}`)\n**Removed by:** {ctx.author.mention}\n**Time:** {self.get_timestamp()}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to remove that role.", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {e}", ephemeral=True)


async def setup(bot):
    await bot.add_cog(ReactionRoles(bot))