import discord
from colour import Color
from pymongo import MongoClient
from dotenv import load_dotenv
import os

from discord import ui, ButtonStyle, Colour

load_dotenv()
mongo = MongoClient(os.getenv("MONGODB_URL"))
main_db = mongo["AAT"]
roles_db = main_db["roles"]

def has_role(user: discord.Member, role: discord.Role) -> bool:
    return any(r.id == role.id for r in user.roles)

def parse_color(color_str: str) -> discord.Color:
    try:
        c = Color(color_str)
        r, g, b = [int(x*255) for x in c.rgb]
        return discord.Color.from_rgb(r, g, b)
    except Exception:
        raise ValueError("Invalid color format")

def get_valid_roles(user_data, ctx):
    """Filter out deleted roles from user's role list"""
    if not user_data or not user_data.get("roles"):
        return None

    valid_roles = []
    guild = ctx.guild
    if guild is None:
        return None

    for role_id in user_data.get("roles", []):
        role = guild.get_role(role_id)
        if role:
            valid_roles.append(role_id)

    # Update MongoDB
    if len(valid_roles) != len(user_data.get("roles", [])):
        if valid_roles:
            roles_db.update_one(
                {"user_id": ctx.author.id},
                {"$set": {"roles": valid_roles}}
            )
        else:
            roles_db.delete_one({"user_id": ctx.author.id})

    return valid_roles if valid_roles else None

from discord import ui, ButtonStyle, Colour

def make_container(*components, accent_color: int | Colour = discord.Color.yellow()):
    view = ui.LayoutView(timeout=120)
    container = ui.Container(accent_color=accent_color)
    for component in components:
        container.add_item(component)
    view.add_item(container)
    return view
