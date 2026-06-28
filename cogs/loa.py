import discord
from discord.ext import commands

from utils.variables import admin

LOA_ROLE_ID = 1292814355921899603
ABUSING_ROLE_ID = 1264032059144540191

class LOA(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="loa", description="Take a leave of absence")
    async def loa(self, ctx: commands.Context):
        if any(r.id in admin for r in ctx.author.roles) or ctx.author.guild_permissions.administrator:
            loa_role = ctx.guild.get_role(LOA_ROLE_ID)
            abusing_role = ctx.guild.get_role(ABUSING_ROLE_ID)

            if loa_role is None:
                await ctx.send("Failed to locate LOA role.")
                return

            if loa_role in ctx.author.roles:
                await ctx.send("You already have the LOA role.")
                return

            # Add LOA role
            await ctx.author.add_roles(loa_role)

            # Remove abusing role if they have it
            if abusing_role is not None and abusing_role in ctx.author.roles:
                await ctx.author.remove_roles(abusing_role)

            # Update nickname with [LOA] tag
            try:
                current_name = ctx.author.display_name
                if "[LOA]" not in current_name:
                    new_name = f"{current_name} [LOA]"
                    await ctx.author.edit(nick=new_name)
            except discord.Forbidden:
                await ctx.send("I don't have permission to change your nickname.")
            except Exception:
                pass

            await ctx.send(f"✅ You have been granted LOA. Your abusing role has been removed and your name has been updated.")
        else:
            await ctx.send("You do not have permission to use this command.")

    @commands.command(name="unloa", description="Return from leave of absence")
    async def unloa(self, ctx: commands.Context):
        loa_role = ctx.guild.get_role(LOA_ROLE_ID)

        if loa_role is None:
            await ctx.send("Failed to locate LOA role.")
            return

        if loa_role not in ctx.author.roles:
            await ctx.send("You do not have the LOA role.")
            return

        # Remove LOA role
        await ctx.author.remove_roles(loa_role)

        # Remove [LOA] from nickname
        try:
            current_name = ctx.author.display_name
            if "[LOA]" in current_name:
                new_name = current_name.replace(" [LOA]", "").replace("[LOA]", "")
                await ctx.author.edit(nick=new_name)
        except discord.Forbidden:
            await ctx.send("I don't have permission to change your nickname.")
        except Exception:
            pass

        await ctx.send(f" <:Leave:1492365946688639148> You have been removed from LOA. Welcome back!")


async def setup(bot):
    await bot.add_cog(LOA(bot))