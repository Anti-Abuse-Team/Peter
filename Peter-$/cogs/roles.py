
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from utils.functions import gen_unique_key, parse_color
from utils.variables import admin
from views.Keys.KeyHelpView import CustomHelpView

load_dotenv()

mongo = MongoClient(os.getenv("MONGODB_URL"))
main_db = mongo["AAT"]
roles_db = main_db["roles"]
keys_db = main_db["keys"]


async def send_response(ctx: commands.Context, *, content=None, embed=None, view=None, ephemeral=False):
    if ctx.interaction:
        return await ctx.send(content=content, embed=embed, view=view, ephemeral=ephemeral)
    return await ctx.send(content=content, embed=embed, view=view)


def is_staff(member: discord.Member) -> bool:
    return any(role.id in admin for role in member.roles) or member.id == 777616657040408606


def get_valid_roles(user_data, ctx):
    if not user_data or not user_data.get("roles"):
        return None

    valid_roles = [role_id for role_id in user_data.get("roles", []) if ctx.guild.get_role(role_id)]

    if len(valid_roles) != len(user_data.get("roles", [])):
        if valid_roles:
            roles_db.update_one({"user_id": ctx.author.id}, {"$set": {"roles": valid_roles}})
        else:
            roles_db.delete_one({"user_id": ctx.author.id})

    return valid_roles if valid_roles else None


class RoleSelect(discord.ui.Select):
    def __init__(self, user_roles, ctx):
        self.ctx = ctx
        options = []

        for i, role_id in enumerate(user_roles):
            role = ctx.guild.get_role(role_id)
            if role:
                options.append(
                    discord.SelectOption(
                        label=f"Role {i + 1}: {role.name}",
                        value=str(role_id),
                    )
                )

        if not options:
            options.append(
                discord.SelectOption(
                    label="No valid roles",
                    value="0",
                    disabled=True,
                )
            )

        super().__init__(
            placeholder="Select a role to configure",
            options=options,
            min_values=1,
            max_values=1,
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("You cannot use this menu!", ephemeral=True)
            return

        self.view.selected_role_id = int(self.values[0])
        await interaction.response.defer()
        self.view.stop()


class RoleSelectView(discord.ui.View):
    def __init__(self, user_roles, ctx):
        super().__init__(timeout=30)
        self.user_roles = user_roles
        self.ctx = ctx
        self.selected_role_id = None
        self.add_item(RoleSelect(user_roles, ctx))


class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group()
    async def custom(self, ctx: commands.Context):
        return

    @custom.command(name="register", description="Registers a custom role to a user")
    async def register(self, ctx: commands.Context, role: discord.Role, member: discord.Member):
        if not is_staff(ctx.author):
            embed = discord.Embed(
                title="<:Cross:1490727525356278064> Lack of Permissions",
                description="You do not have permission to execute this command.",
                color=discord.Color.red(),
            )
            await send_response(ctx, embed=embed, ephemeral=True)
            return

        try:
            roles_db.insert_one({"user_id": member.id, "roles": [role.id]})
            embed = discord.Embed(
                title="<:Check:1490727471761457335> Registered",
                description=f"{role.mention} has been registered for {member.mention}",
                color=discord.Color.green(),
            )
            await send_response(ctx, embed=embed)
        except PyMongoError as exc:
            embed = discord.Embed(
                title="<:Cross:1490727525356278064> Failed to Register",
                description=f"I have received an error. (`{exc}`)",
                color=discord.Color.red(),
            )
            await send_response(ctx, embed=embed)

    @custom.command(name="create", description="Creates a custom role")
    async def create(self, ctx: commands.Context, name: str):
        if ctx.author.premium_since is None and not ctx.author.guild_permissions.administrator:
            embed = discord.Embed(
                title="<:Cross:1490727525356278064> Not Allowed",
                description="You are not allowed to create a custom role as you are not a server booster.",
                color=discord.Color.red(),
            )
            await send_response(ctx, embed=embed, ephemeral=True)
            return

        info = roles_db.find_one({"user_id": ctx.author.id})
        valid_roles = get_valid_roles(info, ctx)

        if valid_roles and len(valid_roles) >= 2:
            embed = discord.Embed(
                title="<:Cross:1490727525356278064> Role Limit",
                description="You are only allowed to have 2 custom roles at this time.",
                color=discord.Color.red(),
            )
            await send_response(ctx, embed=embed, ephemeral=True)
            return

        role = await ctx.guild.create_role(name=name)

        try:
            await ctx.guild.edit_role_positions({role: 154})
        except discord.HTTPException as exc:
            print(f"Warning: Could not reposition role: {exc}")

        await ctx.author.add_roles(role)

        if valid_roles:
            roles_db.update_one({"user_id": ctx.author.id}, {"$push": {"roles": role.id}})
        else:
            roles_db.insert_one({"user_id": ctx.author.id, "roles": [role.id]})

        embed = discord.Embed(
            title="<:Check:1490727471761457335> Role Created",
            description=f"I have successfully created {role.mention}",
            color=discord.Color.green(),
        )
        await send_response(ctx, embed=embed, ephemeral=True)

    @custom.command(name="color", description="Modifies the color of a custom role")
    async def color(self, ctx: commands.Context, color: str):
        info = roles_db.find_one({"user_id": ctx.author.id})
        valid_roles = get_valid_roles(info, ctx)

        if not valid_roles:
            embed = discord.Embed(
                title="<:Cross:1490727525356278064> No Role",
                description="You do not currently have any custom role registered.",
                color=discord.Color.red(),
            )
            await send_response(ctx, embed=embed, ephemeral=True)
            return

        if len(valid_roles) > 1:
            view = RoleSelectView(valid_roles, ctx)
            await send_response(ctx, content="Select which role you want to modify:", view=view, ephemeral=True)
            await view.wait()

            selected_role_id = view.selected_role_id
            if not selected_role_id:
                await send_response(ctx, content="No role selected.", ephemeral=True)
                return
        else:
            selected_role_id = valid_roles[0]

        try:
            role_color = parse_color(color)
        except Exception:
            await send_response(ctx, content="Invalid hex code.", ephemeral=True)
            return

        role = ctx.guild.get_role(selected_role_id)
        if role is None:
            await send_response(ctx, content="Could not fetch role.", ephemeral=True)
            return

        await role.edit(color=role_color)
        embed = discord.Embed(
            title="<:Check:1490727471761457335> Color Changed",
            description=f"Successfully changed role color to `{color}`",
            color=discord.Color.green(),
        )
        await send_response(ctx, embed=embed, ephemeral=True)

    @custom.command(name="name", description="Modifies the name of a custom role")
    async def name(self, ctx: commands.Context, *, name: str):
        info = roles_db.find_one({"user_id": ctx.author.id})
        valid_roles = get_valid_roles(info, ctx)

        if not valid_roles:
            embed = discord.Embed(
                title="<:Cross:1490727525356278064> No Role Found",
                description="You do not currently have any custom role registered.",
                color=discord.Color.red(),
            )
            await send_response(ctx, embed=embed, ephemeral=True)
            return

        if len(valid_roles) > 1:
            view = RoleSelectView(valid_roles, ctx)
            await send_response(ctx, content="Select which role you want to modify:", view=view, ephemeral=True)
            await view.wait()

            selected_role_id = view.selected_role_id
            if not selected_role_id:
                await send_response(ctx, content="No role selected.", ephemeral=True)
                return
        else:
            selected_role_id = valid_roles[0]

        role = ctx.guild.get_role(selected_role_id)
        if role is None:
            await send_response(ctx, content="Could not fetch role.", ephemeral=True)
            return

        await role.edit(name=name)
        embed = discord.Embed(
            title="<:Check:1490727471761457335> Name Changed",
            description=f"Successfully changed role name to `{name}`",
            color=discord.Color.green(),
        )
        await send_response(ctx, embed=embed, ephemeral=True)

    @custom.command(name="icon", description="Modifies the icon of a custom role")
    async def icon(self, ctx: commands.Context, icon: discord.Attachment):
        info = roles_db.find_one({"user_id": ctx.author.id})
        valid_roles = get_valid_roles(info, ctx)

        if not valid_roles:
            embed = discord.Embed(
                title="<:Cross:1490727525356278064> No Role Found",
                description="You do not currently have any custom role registered.",
                color=discord.Color.red(),
            )
            await send_response(ctx, embed=embed, ephemeral=True)
            return

        if len(valid_roles) > 1:
            view = RoleSelectView(valid_roles, ctx)
            await send_response(ctx, content="Select which role you want to modify:", view=view, ephemeral=True)
            await view.wait()

            selected_role_id = view.selected_role_id
            if not selected_role_id:
                await send_response(ctx, content="No role selected.", ephemeral=True)
                return
        else:
            selected_role_id = valid_roles[0]

        if not icon.content_type or not icon.content_type.startswith("image/"):
            await send_response(ctx, content="❌ Please upload a valid image file.", ephemeral=True)
            return

        role = ctx.guild.get_role(selected_role_id)
        if role is None:
            await send_response(ctx, content="Could not fetch role.", ephemeral=True)
            return

        image_bytes = await icon.read()
        try:
            await role.edit(display_icon=image_bytes)
        except Exception as exc:
            await send_response(ctx, content=f"❌ Failed to set icon: {exc}", ephemeral=True)
            return

        embed = discord.Embed(
            title="<:Check:1490727471761457335> Icon Changed",
            description="Successfully changed role icon.",
            color=discord.Color.green(),
        )
        embed.set_thumbnail(url=icon.url)
        await send_response(ctx, embed=embed, ephemeral=True)

    @commands.hybrid_group()
    async def key(self, ctx: commands.Context):
        return

    @key.command(name="give", description="Give role via key to specific member (staff)")
    async def key_give(self, ctx: commands.Context, role: discord.Role, member: discord.Member, uses: int = 1):
        if not is_staff(ctx.author):
            embed = discord.Embed(
                title="❌ No Permission",
                description="Staff only.",
                color=discord.Color.red(),
            )
            await send_response(ctx, embed=embed, ephemeral=True)
            return

        try:
            key_str = gen_unique_key(keys_db)
            keys_db.insert_one(
                {
                    "key": key_str,
                    "role_id": role.id,
                    "guild_id": ctx.guild.id,
                    "uses_left": uses,
                    "assigned_to": member.id,
                    "claimed_by": [],
                }
            )
            embed = discord.Embed(
            title="✅ Key Generated",
                description=f"**Key:** `{key_str}`\n**Role:** {role.mention}\n**Uses:** {uses}",
                color=discord.Color.green(),
            )
            await send_response(ctx, embed=embed, ephemeral=True)
        except PyMongoError as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to create key: {str(e)}",
                color=discord.Color.red(),
            )
            await send_response(ctx, embed=embed, ephemeral=True)

    @key.command(name="claim", description="Claim a key for custom role")
    async def key_claim(self, ctx: commands.Context, key: str):
        key_doc = keys_db.find_one({"key": key, "guild_id": ctx.guild.id})

        if not key_doc:
            embed = discord.Embed(
                title="❌ Invalid Key",
                description="Key not found or wrong server.",
                color=discord.Color.red(),
            )
            await send_response(ctx, embed=embed, ephemeral=True)
            return

        # Private key check
        if "assigned_to" in key_doc and key_doc["assigned_to"] != ctx.author.id:
            embed = discord.Embed(
                title="❌ Private Key",
                description="This is a private key assigned to someone else.",
                color=discord.Color.red(),
            )
            await send_response(ctx, embed=embed, ephemeral=True)
            return

        if key_doc["uses_left"] <= 0:
            embed = discord.Embed(
                title="❌ No Uses",
                description="Key has no remaining uses.",
                color=discord.Color.red(),
            )
            await send_response(ctx, embed=embed, ephemeral=True)
            return

        role = ctx.guild.get_role(key_doc["role_id"])
        if not role:
            embed = discord.Embed(
                title="❌ Role Missing",
                description="Role was deleted.",
                color=discord.Color.red(),
            )
            keys_db.delete_one({"key": key})
            await send_response(ctx, embed=embed, ephemeral=True)
            return

        if role in ctx.author.roles:
            embed = discord.Embed(
                title="❌ Already Have",
                description="You already have this role.",
                color=discord.Color.red(),
            )
            await send_response(ctx, embed=embed, ephemeral=True)
            return

        try:
            await ctx.author.add_roles(role, reason="Key claim")

            user_doc = roles_db.find_one({"user_id": ctx.author.id})
            if user_doc:
                if role.id not in user_doc.get("roles", []):
                    roles_db.update_one({"user_id": ctx.author.id}, {"$push": {"roles": role.id}})
            else:
                roles_db.insert_one({"user_id": ctx.author.id, "roles": [role.id]})

            keys_db.update_one(
                {"key": key},
                {"$inc": {"uses_left": -1}, "$push": {"claimed_by": ctx.author.id}},
            )

            embed = discord.Embed(
                title="✅ Role Claimed",
                description=f"You now have {role.mention}!",
                color=discord.Color.green(),
            )
            await send_response(ctx, embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Claim Failed",
                description=str(e),
                color=discord.Color.red(),
            )
            await send_response(ctx, embed=embed, ephemeral=True)

    @custom.command(name="delete", description="Delete one of your custom roles")
    async def custom_delete(self, ctx: commands.Context):
        info = roles_db.find_one({"user_id": ctx.author.id})
        valid_roles = get_valid_roles(info, ctx)

        if not valid_roles:
            embed = discord.Embed(
                title="❌ No Roles",
                description="No custom roles to delete.",
                color=discord.Color.red(),
            )
            await send_response(ctx, embed=embed, ephemeral=True)
            return

        if len(valid_roles) > 1:
            view = RoleSelectView(valid_roles, ctx)
            await send_response(ctx, content="Select role to delete:", view=view, ephemeral=True)
            await view.wait()

            if not view.selected_role_id:
                return
            selected_id = view.selected_role_id
        else:
            selected_id = valid_roles[0]

        role_obj = ctx.guild.get_role(selected_id)
        roles_db.update_one({"user_id": ctx.author.id}, {"$pull": {"roles": selected_id}})

        if role_obj:
            await ctx.author.remove_roles(role_obj)

        embed = discord.Embed(
            title="✅ Deleted",
            description="Role removed from your account.",
            color=discord.Color.green(),
        )
        await send_response(ctx, embed=embed, ephemeral=True)

        info = roles_db.find_one({"user_id": ctx.author.id})
        if not get_valid_roles(info, ctx):
            roles_db.delete_one({"user_id": ctx.author.id})

    @custom.command(name="help", description="View paginated custom role help")
    async def custom_help(self, ctx: commands.Context):
        pages = [
            discord.Embed(
                title="📝 Create",
                description="`custom create <name>`\nCreate your own role (max 2, boosters/admins).",
                color=discord.Color.blue(),
            ),
            discord.Embed(
                title="🛠️ Manage",
                description="`custom color <hex>`\n`custom name <new name>`\n`custom icon <attach>`\n`custom delete`",
                color=discord.Color.green(),
            ),
            discord.Embed(
                title="👥 Staff",
                description="`custom register <@role> <@member>`\n`key give <@role> [uses]`",
                color=discord.Color.orange(),
            ),
            discord.Embed(
                title="🎁 Keys",
                description="`key claim <paste_key>`\nClaim roles from giveaways/events.",
                color=discord.Color.purple(),
            ),
        ]

        for i, embed in enumerate(pages):
            embed.set_footer(text=f"Page {i + 1}/4")

        view = CustomHelpView(pages, ctx)
        await send_response(ctx, embed=pages[0], view=view, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Roles(bot))