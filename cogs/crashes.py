import discord
from discord.ext import commands
import pymongo
from pymongo import MongoClient
from dotenv import load_dotenv
import os

from pymongo.errors import PyMongoError

from utils.variables import admin
from utils.functions import get_valid_roles, make_container
from views.Crashes.CrashSelection import CrashSelection

from discord import ui

load_dotenv()

mongo = MongoClient(os.getenv("MONGODB_URL"))
main_db = mongo["AAT"]
crashes_db = main_db["crashes"]

class Crashes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group()
    async def crashes(self, ctx: commands.Context):
        return
    
    @crashes.command(name="register", description="Registers a crash to a specific user")
    async def register(self, ctx: commands.Context, user: discord.Member, crash: discord.Role):    
        if any(r.id in admin for r in ctx.author.roles) or ctx.author.guild_permissions.administrator:
            info = crashes_db.find_one({"user_id": user.id})
            if info:
                crashes_db.update_one({"user_id": user.id}, {"$push": {"roles": crash.id}})
            else:
                crashes_db.insert_one({"user_id": user.id, "roles": [crash.id]})
            view = make_container(
                ui.TextDisplay("### <:Check:1492629423600570508> Registered"),
                ui.Separator(),
                ui.TextDisplay(f"I have succesfully registered `{crash.name}` to `{user.name}`"),
                accent_color=discord.Color.green()
            )
            await ctx.send(view=view)
        else:
            view = make_container(
                ui.TextDisplay("### <:Cross:1492630473845772548> No Permission"),
                ui.Separator(),
                ui.TextDisplay("You do not have permisson to execute this command."),
                accent_color=discord.Color.red()
            )
            await ctx.send(view=view, ephemeral=True)   

    @crashes.command(name="issue", description="Issue another user one of your crashe roles")  
    async def issue(self, ctx: commands.Context, user: discord.Member):
        info = crashes_db.find_one({"user_id": ctx.author.id})
        roles = []

        if info is None:
            view = make_container(
                ui.TextDisplay("### <:Cross:1492630473845772548> No Roles Found"),
                ui.Separator(),
                ui.TextDisplay("I was not able to locate any roles under your information."),
                accent_color=discord.Color.red()
            )
            await ctx.send(view=view, ephemeral=True)            

        for role_id in info.get("roles", []):
            roles.append(role_id)

        if len(roles) > 1:
            view = CrashSelection(roles, ctx)
            await ctx.send(view=view, ephemeral=True)
            await view.wait()
            selected_role_id = view.selected_role_id

            role = ctx.guild.get_role(selected_role_id)
            await user.add_roles(role)
            view = make_container(
                ui.TextDisplay("### <:Check:1492629423600570508> Role Added"),
                ui.Separator(),
                ui.TextDisplay("I have succesfully added the crash."),
                accent_color=discord.Color.green()
            )
            await ctx.send(view=view, ephemeral=True)

            log_channel = ctx.guild.get_channel(1492638575928414279)

            log = make_container(
                ui.TextDisplay("### <:Alert:1492637717798981702> Crash"),
                ui.Separator(),
                ui.TextDisplay(f"Command: `/crash issue`\nHandler: {ctx.author.name}\nCrash: `{role.name}`\nIssued to: {user.name}"),
                accent_color=0xF9A825
            )

            await log_channel.send(view=log)
        else:
            role_id = int(roles[0])
            role = ctx.guild.get_role(role_id)
            await user.add_roles(role)
            view = make_container(
                ui.TextDisplay("### <:Check:1492629423600570508> Role Added"),
                ui.Separator(),
                ui.TextDisplay("I have succesfully added the crash."),
                accent_color=discord.Color.green()
            )
            await ctx.send(view=view, ephemeral=True)
        
            log_channel = ctx.guild.get_channel(1492638575928414279)

            log = make_container(
                ui.TextDisplay("### <:Alert:1492637717798981702> Crash"),
                ui.Separator(),
                ui.TextDisplay(f"Command: `/crash issue`\nHandler: {ctx.author.name}\nCrash: `{role.name}`\nIssued to: {user.name}"),
                accent_color=0xF9A825
            )

            await log_channel.send(view=log)
    
async def setup(bot):
    await bot.add_cog(Crashes(bot))
