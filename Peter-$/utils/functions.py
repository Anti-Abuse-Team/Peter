import discord
from discord.ext import commands
from colour import Color

def has_role(user: discord.Member, role: discord.Role) -> bool:
    return any(r.id == role.id for r in user.roles)

def parse_color(color_str: str) -> discord.Color:
    try:
        c = Color(color_str)
        r, g, b = [int(x*255) for x in c.rgb]
        return discord.Color.from_rgb(r, g, b)
    except Exception:
        raise ValueError("Invalid color format")
