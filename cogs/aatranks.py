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

    @commands.hybrid_command(name="senioragent", description="Adds the AAT Senior Agent role to a user")
    async def senioragent(self, ctx: commands.Context, user: discord.Member):
        """Adds the AAT Senior Agent role to a user"""
        if not self.is_trial_overseer(ctx):
            return await ctx.send("You do not have permission to use this command.", ephemeral=True)
        await self.add_role(ctx, user, "senioragent", "AAT Senior Agent")

    @commands.hybrid_command(name="aatsenioragent", description="Adds the AAT Senior Special Agent role to a user")
    async def aatsenioragent(self, ctx: commands.Context, user: discord.Member):
        """Adds the AAT Senior Special Agent role to a user"""
        if not self.is_trial_overseer(ctx):
            return await ctx.send("You do not have permission to use this command.", ephemeral=True)
        await self.add_role(ctx, user, "aatsenioragent", "AAT Senior Special Agent")

    # ============================================================
    # REMOVE AAT RANK COMMANDS (Trial Overseer)
    # ============================================================

    @commands.hybrid_command(name="raatmember", description="Removes the AAT Member role from a user")
    async def raatmember(self, ctx: commands.Context, user: discord.Member):
        """Removes the AAT Member role from a user"""
        if not self.is_trial_overseer(ctx):
            return await ctx.send("You do not have permission to use this command.", ephemeral=True)
        await self.remove_role(ctx, user, "aat_member", "AAT Member")

    @commands.hybrid_command(name="rofficer", description="Removes the AAT Officer role from a user")
    async def rofficer(self, ctx: commands.Context, user: discord.Member):
        """Removes the AAT Officer role from a user"""
        if not self.is_trial_overseer(ctx):
            return await ctx.send("You do not have permission to use this command.", ephemeral=True)
        await self.remove_role(ctx, user, "officer", "AAT Officer")

    @commands.hybrid_command(name="rspecialagent", description="Removes the AAT Special Agent role from a user")
    async def rspecialagent(self, ctx: commands.Context, user: discord.Member):
        """Removes the AAT Special Agent role from a user"""
        if not self.is_trial_overseer(ctx):
            return await ctx.send("You do not have permission to use this command.", ephemeral=True)
        await self.remove_role(ctx, user, "specialagent", "AAT Special Agent")

    @commands.hybrid_command(name="ragent", description="Removes the AAT Agent role from a user")
    async def ragent(self, ctx: commands.Context, user: discord.Member):
        """Removes the AAT Agent role from a user"""
        if not self.is_trial_overseer(ctx):
            return await ctx.send("You do not have permission to use this command.", ephemeral=True)
        await self.remove_role(ctx, user, "agent", "AAT Agent")

    @commands.hybrid_command(name="rrecruit", description="Removes the AAT Recruit role from a user")
    async def rrecruit(self, ctx: commands.Context, user: discord.Member):
        """Removes the AAT Recruit role from a user"""
        if not self.is_trial_overseer(ctx):
            return await ctx.send("You do not have permission to use this command.", ephemeral=True)
        await self.remove_role(ctx, user, "recruit", "AAT Recruit")

    @commands.hybrid_command(name="rjunioragent", description="Removes the AAT Junior Agent role from a user")
    async def rjunioragent(self, ctx: commands.Context, user: discord.Member):
        """Removes the AAT Junior Agent role from a user"""
        if not self.is_trial_overseer(ctx):
            return await ctx.send("You do not have permission to use this command.", ephemeral=True)
        await self.remove_role(ctx, user, "junioragent", "AAT Junior Agent")

    @commands.hybrid_command(name="rsenioragent", description="Removes the AAT Senior Agent role from a user")
    async def rsenioragent(self, ctx: commands.Context, user: discord.Member):
        """Removes the AAT Senior Agent role from a user"""
        if not self.is_trial_overseer(ctx):
            return await ctx.send("You do not have permission to use this command.", ephemeral=True)
        await self.remove_role(ctx, user, "senioragent", "AAT Senior Agent")

    @commands.hybrid_command(name="raatsenioragent", description="Removes the AAT Senior Special Agent role from a user")
    async def raatsenioragent(self, ctx: commands.Context, user: discord.Member):
        """Removes the AAT Senior Special Agent role from a user"""
        if not self.is_trial_overseer(ctx):
            return await ctx.send("You do not have permission to use this command.", ephemeral=True)
        await self.remove_role(ctx, user, "aatsenioragent", "AAT Senior Special Agent")

    async def remove_all_rank_auths(self, ctx, user: discord.Member):
        """Remove all AAT rank and auth roles from a user"""
        rank_keys = [
            "aat_member", "trial_aat", "unoffical_aat",
            "officer", "specialagent", "agent", "recruit",
            "junioragent", "senioragent", "aatsenioragent",
            "auth-1", "auth-2", "auth-3", "auth-4",
            "auth-1_cap", "auth-2_cap", "auth-3_cap", "auth-4_cap"
        ]
        removed = []
        for key in rank_keys:
            role = ctx.guild.get_role(role_ids[key])
            if role is not None and role in user.roles:
                try:
                    await user.remove_roles(role, reason=f"Removed by suspension from {ctx.author} ({ctx.author.id})")
                    removed.append(f"`{role.name}`")
                except discord.Forbidden:
                    pass
        return removed

    # ============================================================
    # SUSPEND / UNSUSPEND COMMANDS (Trial Overseer)
    # ============================================================

    @commands.hybrid_command(name="suspend", description="Suspends a user (adds suspended role, removes all ranks/auths)")
    async def suspend(self, ctx: commands.Context, user: discord.Member):
        """Suspends a user - adds suspended role and removes all ranks/auths"""
        if not self.is_trial_overseer(ctx):
            return await ctx.send("You do not have permission to use this command.", ephemeral=True)

        suspended_role = ctx.guild.get_role(role_ids["suspended"])
        if suspended_role is None:
            embed = discord.Embed(
                title="<:Cross:1490727525356278064> Role Not Found",
                description="Could not find the `Suspended` role.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed, ephemeral=True)

        if suspended_role not in user.roles:
            try:
                await user.add_roles(suspended_role, reason=f"Suspended by {ctx.author} ({ctx.author.id})")
            except discord.Forbidden:
                embed = discord.Embed(
                    title="<:Cross:1490727525356278064> Missing Permissions",
                    description="I don't have permission to add the suspended role.",
                    color=discord.Color.red()
                )
                return await ctx.send(embed=embed, ephemeral=True)

        # Remove all ranks and auths
        removed = await self.remove_all_rank_auths(ctx, user)

        embed = discord.Embed(
            title="<:Check:1490727471761457335> User Suspended",
            description=f"**User:** {user.mention} (`{user.id}`)\n**Suspended by:** {ctx.author.mention}\n**Roles removed:** {', '.join(removed) if removed else 'None'}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="unsuspend", description="Unsuspends a user (removes suspended role)")
    async def unsuspend(self, ctx: commands.Context, user: discord.Member):
        """Unsuspends a user - removes the suspended role only (does not restore ranks/auths)"""
        if not self.is_trial_overseer(ctx):
            return await ctx.send("You do not have permission to use this command.", ephemeral=True)
        await self.remove_role(ctx, user, "suspended", "Suspended")

    # ============================================================
    # VERIFY COMMAND (Trial Overseer)
    # ============================================================

    @commands.hybrid_command(name="verify", description="Verifies a user (adds server access and unofficial AAT roles)")
    async def verify(self, ctx: commands.Context, user: discord.Member):
        """Verifies a user - adds server access and unofficial AAT roles"""
        if not self.is_trial_overseer(ctx):
            return await ctx.send("You do not have permission to use this command.", ephemeral=True)

        added = []
        for key, label in [("server_access", "Server Access"), ("unoffical_aat", "Unofficial AAT")]:
            role = ctx.guild.get_role(role_ids[key])
            if role is None:
                embed = discord.Embed(
                    title="<:Cross:1490727525356278064> Role Not Found",
                    description=f"Could not find the `{label}` role.",
                    color=discord.Color.red()
                )
                return await ctx.send(embed=embed, ephemeral=True)

            if role in user.roles:
                continue

            try:
                await user.add_roles(role, reason=f"Verified by {ctx.author} ({ctx.author.id})")
                added.append(f"`{role.name}`")
            except discord.Forbidden:
                embed = discord.Embed(
                    title="<:Cross:1490727525356278064> Missing Permissions",
                    description=f"I don't have permission to add the `{label}` role.",
                    color=discord.Color.red()
                )
                return await ctx.send(embed=embed, ephemeral=True)

        if not added:
            embed = discord.Embed(
                title="<:Cross:1490727525356278064> Already Verified",
                description=f"{user.mention} already has both verification roles.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed, ephemeral=True)

        embed = discord.Embed(
            title="<:Check:1490727471761457335> User Verified",
            description=f"**User:** {user.mention} (`{user.id}`)\n**Verified by:** {ctx.author.mention}\n**Roles added:** {', '.join(added)}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    # ============================================================
    # REVIEW / UNREVIEW COMMANDS (Trial Overseer)
    # ============================================================

    @commands.hybrid_command(name="review", description="Adds the Under Review role to a user")
    async def review(self, ctx: commands.Context, user: discord.Member):
        """Adds the Under Review role to a user"""
        if not self.is_trial_overseer(ctx):
            return await ctx.send("You do not have permission to use this command.", ephemeral=True)
        await self.add_role(ctx, user, "under_review", "Under Review")

    @commands.hybrid_command(name="unreview", description="Removes the Under Review role from a user")
    async def unreview(self, ctx: commands.Context, user: discord.Member):
        """Removes the Under Review role from a user"""
        if not self.is_trial_overseer(ctx):
            return await ctx.send("You do not have permission to use this command.", ephemeral=True)
        await self.remove_role(ctx, user, "under_review", "Under Review")


async def setup(bot):
    await bot.add_cog(AATRanks(bot))
