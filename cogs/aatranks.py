import discord
from discord.ext import commands

from utils.variables import role_ids, admin


class AATRanks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_admin(self, ctx) -> bool:
        """Check if user has admin permissions"""
        return any(r.id in admin for r in ctx.author.roles) or ctx.author.guild_permissions.administrator

    def is_auth_manager(self, ctx) -> bool:
        """Check if user is an auth manager or admin"""
        return any(r.id == role_ids["auth_manager"] for r in ctx.author.roles) or self.is_admin(ctx)

    def is_trial_overseer(self, ctx) -> bool:
        """Check if user is a trial overseer (demo inspector) or admin"""
        return any(r.id == role_ids["trial_overseer"] for r in ctx.author.roles) or self.is_admin(ctx)

    async def add_role(self, ctx, user: discord.Member, role_key: str, role_name: str):
        """Helper to add a role to a user"""
        role = ctx.guild.get_role(role_ids[role_key])
        if role is None:
            embed = discord.Embed(
                title="<:Cross:1490727525356278064> Role Not Found",
                description=f"Could not find the `{role_name}` role. Please contact a developer.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        if role in user.roles:
            embed = discord.Embed(
                title="<:Cross:1490727525356278064> Already Has Role",
                description=f"{user.mention} already has the {role.mention} role.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        try:
            await user.add_roles(role, reason=f"{role_name} added by {ctx.author} ({ctx.author.id})")
            embed = discord.Embed(
                title="<:Check:1490727471761457335> Role Added",
                description=f"**User:** {user.mention} (`{user.id}`)\n**Role:** {role.mention}\n**Added by:** {ctx.author.mention}",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except discord.Forbidden:
            embed = discord.Embed(
                title="<:Cross:1490727525356278064> Missing Permissions",
                description="I don't have permission to add that role. Make sure my role is higher than the target role.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="<:Cross:1490727525356278064> Error",
                description=f"An error occurred: {e}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, ephemeral=True)

    async def remove_role(self, ctx, user: discord.Member, role_key: str, role_name: str):
        """Helper to remove a role from a user"""
        role = ctx.guild.get_role(role_ids[role_key])
        if role is None:
            embed = discord.Embed(
                title="<:Cross:1490727525356278064> Role Not Found",
                description=f"Could not find the `{role_name}` role.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        if role not in user.roles:
            embed = discord.Embed(
                title="<:Cross:1490727525356278064> Doesn't Have Role",
                description=f"{user.mention} doesn't have the {role.mention} role.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        try:
            await user.remove_roles(role, reason=f"{role_name} removed by {ctx.author} ({ctx.author.id})")
            embed = discord.Embed(
                title="<:Check:1490727471761457335> Role Removed",
                description=f"**User:** {user.mention} (`{user.id}`)\n**Role:** {role.mention}\n**Removed by:** {ctx.author.mention}",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
        except discord.Forbidden:
            embed = discord.Embed(
                title="<:Cross:1490727525356278064> Failed Permissions",
                description="I don't have permission to remove that role. Make sure my role is higher than the target role.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="<:Cross:1490727525356278064> Error",
                description=f"An error occurred: {e}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, ephemeral=True)

    # ============================================================
    # AUTH COMMANDS (Auth Manager + Trial Overseer)
    # ============================================================

    @commands.hybrid_command(name="auth1", description="Adds the AUTH 1 role to a user")
    async def auth1(self, ctx: commands.Context, user: discord.Member):
        """Adds the AUTH 1 role to a user"""
        if not (self.is_auth_manager(ctx) or self.is_trial_overseer(ctx)):
            return await ctx.send("You do not have permission to use this command.", ephemeral=True)
        await self.add_role(ctx, user, "auth-1", "AUTH 1")

    @commands.hybrid_command(name="auth2", description="Adds the AUTH 2 role to a user")
    async def auth2(self, ctx: commands.Context, user: discord.Member):
        """Adds the AUTH 2 role to a user"""
        if not (self.is_auth_manager(ctx) or self.is_trial_overseer(ctx)):
            return await ctx.send("You do not have permission to use this command.", ephemeral=True)
        await self.add_role(ctx, user, "auth-2", "AUTH 2")

    @commands.hybrid_command(name="auth3", description="Adds the AUTH 3 role to a user")
    async def auth3(self, ctx: commands.Context, user: discord.Member):
        """Adds the AUTH 3 role to a user"""
        if not (self.is_auth_manager(ctx) or self.is_trial_overseer(ctx)):
            return await ctx.send("You do not have permission to use this command.", ephemeral=True)
        await self.add_role(ctx, user, "auth-3", "AUTH 3")

    @commands.hybrid_command(name="auth4", description="Adds the AUTH 4 role to a user")
    async def auth4(self, ctx: commands.Context, user: discord.Member):
        """Adds the AUTH 4 role to a user"""
        if not (self.is_auth_manager(ctx) or self.is_trial_overseer(ctx)):
            return await ctx.send("You do not have permission to use this command.", ephemeral=True)
        await self.add_role(ctx, user, "auth-4", "AUTH 4")

    # ============================================================
    # AUTH CAP COMMANDS (Auth Manager + Trial Overseer)
    # ============================================================

    @commands.hybrid_command(name="authcap1", description="Adds the AUTH 1 CAP role to a user")
    async def authcap1(self, ctx: commands.Context, user: discord.Member):
        """Adds the AUTH 1 CAP role to a user"""
        if not (self.is_auth_manager(ctx) or self.is_trial_overseer(ctx)):
            return await ctx.send("You do not have permission to use this command.", ephemeral=True)
        await self.add_role(ctx, user, "auth-1_cap", "AUTH 1 CAP")

    @commands.hybrid_command(name="authcap2", description="Adds the AUTH 2 CAP role to a user")
    async def authcap2(self, ctx: commands.Context, user: discord.Member):
        """Adds the AUTH 2 CAP role to a user"""
        if not (self.is_auth_manager(ctx) or self.is_trial_overseer(ctx)):
            return await ctx.send("You do not have permission to use this command.", ephemeral=True)
        await self.add_role(ctx, user, "auth-2_cap", "AUTH 2 CAP")

    @commands.hybrid_command(name="authcap3", description="Adds the AUTH 3 CAP role to a user")
    async def authcap3(self, ctx: commands.Context, user: discord.Member):
        """Adds the AUTH 3 CAP role to a user"""
        if not (self.is_auth_manager(ctx) or self.is_trial_overseer(ctx)):
            return await ctx.send("You do not have permission to use this command.", ephemeral=True)
        await self.add_role(ctx, user, "auth-3_cap", "AUTH 3 CAP")

    @commands.hybrid_command(name="authcap4", description="Adds the AUTH 4 CAP role to a user")
    async def authcap4(self, ctx: commands.Context, user: discord.Member):
        """Adds the AUTH 4 CAP role to a user"""
        if not (self.is_auth_manager(ctx) or self.is_trial_overseer(ctx)):
            return await ctx.send("You do not have permission to use this command.", ephemeral=True)
        await self.add_role(ctx, user, "auth-4_cap", "AUTH 4 CAP")

    # ============================================================
    # REMOVE AUTH COMMANDS (Auth Manager + Trial Overseer)
    # ============================================================

    @commands.hybrid_command(name="rauth", description="Removes an AUTH level role from a user")
    async def rauth(self, ctx: commands.Context, user: discord.Member, level: int):
        """Removes an AUTH level role from a user (level 1-4)"""
        if not (self.is_auth_manager(ctx) or self.is_trial_overseer(ctx)):
            return await ctx.send("You do not have permission to use this command.", ephemeral=True)

        if level not in [1, 2, 3, 4]:
            embed = discord.Embed(
                title="<:Cross:1490727525356278064> Invalid Level",
                description="Please specify a level between 1 and 4.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed, ephemeral=True)

        await self.remove_role(ctx, user, f"auth-{level}", f"AUTH {level}")

    @commands.hybrid_command(name="rauthcap", description="Removes an AUTH CAP level role from a user")
    async def rauthcap(self, ctx: commands.Context, user: discord.Member, level: int):
        """Removes an AUTH CAP level role from a user (level 1-4)"""
        if not (self.is_auth_manager(ctx) or self.is_trial_overseer(ctx)):
            return await ctx.send("You do not have permission to use this command.", ephemeral=True)

        if level not in [1, 2, 3, 4]:
            embed = discord.Embed(
                title="<:Cross:1490727525356278064> Invalid Level",
                description="Please specify a level between 1 and 4.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed, ephemeral=True)

        await self.remove_role(ctx, user, f"auth-{level}_cap", f"AUTH {level} CAP")

    # ============================================================
    # TRIAL COMMANDS (Trial Overseer)
    # ============================================================

    @commands.hybrid_command(name="trial", description="Adds the Trial AAT role to a user")
    async def trial(self, ctx: commands.Context, user: discord.Member):
        """Adds the Trial AAT role to a user"""
        if not self.is_trial_overseer(ctx):
            return await ctx.send("You do not have permission to use this command.", ephemeral=True)
        await self.add_role(ctx, user, "trial_aat", "Trial AAT")

    @commands.hybrid_command(name="-trial", aliases=["untrial"], description="Removes the Trial AAT role from a user")
    async def untrial(self, ctx: commands.Context, user: discord.Member):
        """Removes the Trial AAT role from a user"""
        if not self.is_trial_overseer(ctx):
            return await ctx.send("You do not have permission to use this command.", ephemeral=True)
        await self.remove_role(ctx, user, "trial_aat", "Trial AAT")

    # ============================================================
    # AAT RANK COMMANDS (Trial Overseer)
    # ============================================================

    @commands.hybrid_command(name="aatmember", description="Adds the AAT Member role to a user")
    async def aatmember(self, ctx: commands.Context, user: discord.Member):
        """Adds the AAT Member role to a user"""
        if not self.is_trial_overseer(ctx):
            return await ctx.send("You do not have permission to use this command.", ephemeral=True)
        await self.add_role(ctx, user, "aat_member", "AAT Member")

    @commands.hybrid_command(name="officer", description="Adds the AAT Officer role to a user")
    async def officer(self, ctx: commands.Context, user: discord.Member):
        """Adds the AAT Officer role to a user"""
        if not self.is_trial_overseer(ctx):
            return await ctx.send("You do not have permission to use this command.", ephemeral=True)
        await self.add_role(ctx, user, "officer", "AAT Officer")

    @commands.hybrid_command(name="specialagent", description="Adds the AAT Special Agent role to a user")
    async def specialagent(self, ctx: commands.Context, user: discord.Member):
        """Adds the AAT Special Agent role to a user"""
        if not self.is_trial_overseer(ctx):
            return await ctx.send("You do not have permission to use this command.", ephemeral=True)
        await self.add_role(ctx, user, "specialagent", "AAT Special Agent")

    @commands.hybrid_command(name="agent", description="Adds the AAT Agent role to a user")
    async def agent(self, ctx: commands.Context, user: discord.Member):
        """Adds the AAT Agent role to a user"""
        if not self.is_trial_overseer(ctx):
            return await ctx.send("You do not have permission to use this command.", ephemeral=True)
        await self.add_role(ctx, user, "agent", "AAT Agent")

    @commands.hybrid_command(name="recruit", description="Adds the AAT Recruit role to a user")
    async def recruit(self, ctx: commands.Context, user: discord.Member):
        """Adds the AAT Recruit role to a user"""
        if not self.is_trial_overseer(ctx):
            return await ctx.send("You do not have permission to use this command.", ephemeral=True)
        await self.add_role(ctx, user, "recruit", "AAT Recruit")

    @commands.hybrid_command(name="junioragent", description="Adds the AAT Junior Agent role to a user")
    async def junioragent(self, ctx: commands.Context, user: discord.Member):
        """Adds the AAT Junior Agent role to a user"""
        if not self.is_trial_overseer(ctx):
            return await ctx.send("You do not have permission to use this command.", ephemeral=True)
        await self.add_role(ctx, user, "junioragent", "AAT Junior Agent")


async def setup(bot):
    await bot.add_cog(AATRanks(bot))
