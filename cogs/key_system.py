import discord
from discord.ext import commands
import random
import string

class KeySystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.keys = {}  # Store keys and their associated user IDs

    @commands.command(name='generate_key')
    @commands.has_permissions(manage_roles=True)
    async def generate_key(self, ctx):
        """Generates a random key and sends it to the channel."""
        key = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        self.keys[key] = None  # Initialize the key without an owner
        await ctx.send(f'Generated key: {key}')

    @commands.command(name='claim_key')
    async def claim_key(self, ctx, key: str):
        """Claims a key for the user."""
        if key in self.keys and self.keys[key] is None:
            self.keys[key] = ctx.author.id
            await ctx.send(f'You have claimed the key: {key}')
        else:
            await ctx.send('This key is invalid or has already been claimed.')

    @commands.command(name='delete_key_role')
    @commands.has_permissions(manage_roles=True)
    async def delete_key_role(self, ctx, key: str):
        """Deletes a role associated with a claimed key."""
        user_id = self.keys.get(key)
        if user_id is not None:
            member = ctx.guild.get_member(user_id)
            if member:
                role = discord.utils.get(ctx.guild.roles, name=key)
                if role:
                    await member.remove_roles(role)
                    del self.keys[key]  # Remove the key from the system
                    await ctx.send(f'Removed role associated with key: {key}')
                else:
                    await ctx.send('No role found associated with this key.')
            else:
                await ctx.send('No member found for this key.')
        else:
            await ctx.send('This key is invalid or has not been claimed.')

def setup(bot):
    bot.add_cog(KeySystem(bot))