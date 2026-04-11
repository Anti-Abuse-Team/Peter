import discord
from discord.ext import commands

from utils.variables import admin
from views.ReactionRoles.ReactionRoles import PingReactionRoles, ColorReactionRoles, LeaveReactionRoles

class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group()
    async def reactions(self, ctx: commands.Context):
        return
    
    @reactions.command(name="send", description="Sends reaction roles")
    async def register(self, ctx: commands.Context):    
        if any(r.id in admin for r in ctx.author.roles) or ctx.author.guild_permissions.administrator:
            try:
                view = PingReactionRoles()
                await ctx.send(view=view)
                view = LeaveReactionRoles()
                await ctx.send(view=view)
                view = ColorReactionRoles()
                await ctx.send(view=view)
            except Exception as E:
                await ctx.send(E)
        else:
            await ctx.send('no perms.')
    
    
async def setup(bot):
    await bot.add_cog(ReactionRoles(bot))
