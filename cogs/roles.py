"""
import discord
from discord.ext import commands

from utils.variables import role_ids

class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group()
    async def role(self, ctx: commands.Context):
        return
    
    @role.command(name="add", description="Add a role to a user")
    async def add(self, ctx: commands.Context, user: discord.User, role: discord.Role):
        role_add_perms = {
            role_ids["auth_manager"]: [
                role_ids["auth-1"],
                role_ids["auth-2"],
                role_ids["auth-3"],
                role_ids["auth-4"],
                role_ids["auth-1_cap"],
                role_ids["auth-2_cap"],
                role_ids["auth-3_cap"],
                role_ids["auth-4_cap"]
            ],

            role_ids["demo_inspector"]: [
                role_ids["aat_member"],
                role_ids["trial_aat"],
                role_ids["unoffical_aat"]
            ]
        }

        if any(role.id in role_add_perms for role in ctx.author.roles):
            await ctx.send('pass')
        else:
            return await ctx.send("no perms")
"""