import discord
from discord.ext import commands
from datetime import datetime
import pytz

from utils.databases import roles_db
from utils.variables import role_ids, admin


class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_timestamp(self):
        """Get current timestamp in EST"""
        tz = pytz.timezone("US/Eastern")
        return datetime.now(tz).strftime("%m/%d/%y %I:%M %p")

    def log_to_db(self, user_id: int, role_id: int, role_name: str, action: str, mod_id: int):
        """Log a role action to MongoDB with timestamp, role name, and role ID"""
        timestamp = self.get_timestamp()
        roles_db.insert_one({
            "user_id": user_id,
            "role_id": role_id,
            "role_name": role_name,
            "action": action,
            "moderator_id": mod_id,
            "timestamp": timestamp,
            "full_date": datetime.now(pytz.timezone("US/Eastern")).isoformat()
        })

    def is_admin(self, ctx) -> bool:
        """Check if user has admin permissions"""
        return any(r.id in admin for r in ctx.author.roles) or ctx.author.guild_permissions.administrator

    def is_demo_inspector(self, ctx) -> bool:
        """Check if user is a demo inspector (trial overseer) or admin"""
        return any(r.id == role_ids["demo_inspector"] for r in ctx.author.roles) or self.is_admin(ctx)

    def is_auth_manager(self, ctx) -> bool:
        """Check if user is an auth manager or admin"""
        return any(r.id == role_ids["auth_manager"] for r in ctx.author.roles) or self.is_admin(ctx)

    def get_role_category(self, role_id: int) -> str:
        """Determine if a role is an AAT rank role, auth role, or other"""
        aat_rank_ids = [
            role_ids["aat_member"],
            role_ids["trial_aat"],
            role_ids["unoffical_aat"],
            role_ids["officer"],
            role_ids["specialagent"],
            role_ids["agent"],
            role_ids["recruit"],
            role_ids["junioragent"],
            role_ids["senioragent"],
            role_ids["aatsenioragent"],
            role_ids["suspended"],
            role_ids["server_access"],
            role_ids["under_review"]
        ]
        auth_ids = [
            role_ids["auth-1"],
            role_ids["auth-2"],
            role_ids["auth-3"],
            role_ids["auth-4"],
            role_ids["auth-1_cap"],
            role_ids["auth-2_cap"],
            role_ids["auth-3_cap"],
            role_ids["auth-4_cap"]
        ]

        if role_id in aat_rank_ids:
            return "aat_rank"
        elif role_id in auth_ids:
            return "auth"
        return "other"

    def check_permission(self, ctx, role: discord.Role) -> bool:
        """Check if user has permission to add/remove this role"""
        category = self.get_role_category(role.id)

        if category == "aat_rank":
            return self.is_demo_inspector(ctx)
        elif category == "auth":
            return self.is_auth_manager(ctx)
        else:
            # For other roles, allow admins only
            return self.is_admin(ctx)

    def add_to_persisted(self, user_id: int, role_id: int):
        """Add a role to a user's persisted roles list in the database"""
        roles_db.update_one(
            {"user_id": user_id},
            {"$addToSet": {"persisted_roles": role_id}},
            upsert=True
        )

    def remove_from_persisted(self, user_id: int, role_id: int):
        """Remove a role from a user's persisted roles list in the database"""
        roles_db.update_one(
            {"user_id": user_id},
            {"$pull": {"persisted_roles": role_id}}
        )

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Restore persisted roles when a member rejoins the server"""
        if member.bot:
            return

        try:
            data = roles_db.find_one({"user_id": member.id})
            if not data or not data.get("persisted_roles"):
                return

            guild = member.guild
            to_add = []
            for role_id in data["persisted_roles"]:
                role = guild.get_role(role_id)
                if role is not None and role not in member.roles:
                    to_add.append(role)

            if to_add:
                await member.add_roles(*to_add, reason="Persisted roles restored on rejoin")
                print(f"[+] Restored {len(to_add)} persisted roles for {member} ({member.id})")
        except discord.Forbidden:
            print(f"[-] Could not restore persisted roles for {member} ({member.id}) - missing permissions")
        except Exception as e:
            print(f"[-] Error restoring persisted roles for {member} ({member.id}): {e}")

    @commands.hybrid_group()
    async def role(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid command. Use `/role add`, `/role remove`, or `/rolepersist remove`.")

    @role.command(name="add", description="Add a role to a user (persists for when they rejoin)")
    async def add(self, ctx: commands.Context, user: discord.Member, role: discord.Role):
        """Add a role to a user, persist it, and log it to the database"""
        # Permission check based on role type
        if not self.check_permission(ctx, role):
            category = self.get_role_category(role.id)
            if category == "aat_rank":
                embed = discord.Embed(
                    title="<:Cross:1490727525356278064> Lack of Permissions",
                    description="You need the **Demo Inspector** role to add AAT rank roles.",
                    color=discord.Color.red()
                )
            elif category == "auth":
                embed = discord.Embed(
                    title="<:Cross:1490727525356278064> Lack of Permissions",
                    description="You need the **Auth Manager** role to add auth roles.",
                    color=discord.Color.red()
                )
            else:
                embed = discord.Embed(
                    title="<:Cross:1490727525356278064> Lack of Permissions",
                    description="You do not have permission to add this role.",
                    color=discord.Color.red()
                )
            return await ctx.send(embed=embed, ephemeral=True)

        if role in user.roles:
            return await ctx.send(f"❌ {user.mention} already has the {role.mention} role.", ephemeral=True)

        try:
            await user.add_roles(role, reason=f"Role added by {ctx.author} ({ctx.author.id})")
            self.log_to_db(user.id, role.id, role.name, "add", ctx.author.id)
            self.add_to_persisted(user.id, role.id)

            embed = discord.Embed(
                title="✅ Role Added",
                description=f"**User:** {user.mention} (`{user.id}`)\n**Role:** {role.mention} (`{role.name}` | `{role.id}`)\n**Added by:** {ctx.author.mention}\n**Time:** {self.get_timestamp()}\n**Persisted:** ✅ This role will be restored if they rejoin",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to add that role. Make sure my role is higher than the target role.", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {e}", ephemeral=True)

    @role.command(name="remove", description="Remove a role from a user (removes from persistence)")
    async def remove(self, ctx: commands.Context, user: discord.Member, role: discord.Role):
        """Remove a role from a user, remove from persistence, and log it to the database"""
        # Permission check based on role type
        if not self.check_permission(ctx, role):
            category = self.get_role_category(role.id)
            if category == "aat_rank":
                embed = discord.Embed(
                    title="<:Cross:1490727525356278064> Lack of Permissions",
                    description="You need the **Demo Inspector** role to remove AAT rank roles.",
                    color=discord.Color.red()
                )
            elif category == "auth":
                embed = discord.Embed(
                    title="<:Cross:1490727525356278064> Lack of Permissions",
                    description="You need the **Auth Manager** role to remove auth roles.",
                    color=discord.Color.red()
                )
            else:
                embed = discord.Embed(
                    title="<:Cross:1490727525356278064> Lack of Permissions",
                    description="You do not have permission to remove this role.",
                    color=discord.Color.red()
                )
            return await ctx.send(embed=embed, ephemeral=True)

        if role not in user.roles:
            return await ctx.send(f"❌ {user.mention} doesn't have the {role.mention} role.", ephemeral=True)

        try:
            await user.remove_roles(role, reason=f"Role removed by {ctx.author} ({ctx.author.id})")
            self.log_to_db(user.id, role.id, role.name, "remove", ctx.author.id)
            self.remove_from_persisted(user.id, role.id)

            embed = discord.Embed(
                title="✅ Role Removed",
                description=f"**User:** {user.mention} (`{user.id}`)\n**Role:** {role.mention} (`{role.name}` | `{role.id}`)\n**Removed by:** {ctx.author.mention}\n**Time:** {self.get_timestamp()}\n**Persisted:** ❌ This role will NOT be restored if they rejoin",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to remove that role. Make sure my role is higher than the target role.", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {e}", ephemeral=True)

    @commands.hybrid_group()
    async def rolepersist(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid command. Use `/rolepersist add` or `/rolepersist remove`.")

    @rolepersist.command(name="add", description="Add a role to a user's persisted roles")
    async def persist_add(self, ctx: commands.Context, user: discord.Member, role: discord.Role):
        """Add a role to a user's persisted roles so it's restored when they rejoin"""
        # Permission check based on role type
        if not self.check_permission(ctx, role):
            category = self.get_role_category(role.id)
            if category == "aat_rank":
                embed = discord.Embed(
                    title="<:Cross:1490727525356278064> Lack of Permissions",
                    description="You need the **Demo Inspector** role to persist AAT rank roles.",
                    color=discord.Color.red()
                )
            elif category == "auth":
                embed = discord.Embed(
                    title="<:Cross:1490727525356278064> Lack of Permissions",
                    description="You need the **Auth Manager** role to persist auth roles.",
                    color=discord.Color.red()
                )
            else:
                embed = discord.Embed(
                    title="<:Cross:1490727525356278064> Lack of Permissions",
                    description="You do not have permission to persist this role.",
                    color=discord.Color.red()
                )
            return await ctx.send(embed=embed, ephemeral=True)

        try:
            # Add role to user if they don't have it
            if role not in user.roles:
                await user.add_roles(role, reason=f"Persisted role added by {ctx.author} ({ctx.author.id})")

            self.add_to_persisted(user.id, role.id)
            self.log_to_db(user.id, role.id, role.name, "persist_add", ctx.author.id)

            embed = discord.Embed(
                title="✅ Persisted Role Added",
                description=f"**User:** {user.mention} (`{user.id}`)\n**Role:** {role.mention} (`{role.name}` | `{role.id}`)\n**Added by:** {ctx.author.mention}\n**Time:** {self.get_timestamp()}\n**Persisted:** ✅ This role will be restored if they rejoin",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to add that role.", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {e}", ephemeral=True)

    @rolepersist.command(name="remove", description="Remove a persisted role from a user")
    async def persist_remove(self, ctx: commands.Context, user: discord.Member, role: discord.Role):
        """Remove a role from a user and remove it from persisted roles in the database"""
        # Permission check based on role type
        if not self.check_permission(ctx, role):
            category = self.get_role_category(role.id)
            if category == "aat_rank":
                embed = discord.Embed(
                    title="<:Cross:1490727525356278064> Lack of Permissions",
                    description="You need the **Demo Inspector** role to remove AAT rank roles.",
                    color=discord.Color.red()
                )
            elif category == "auth":
                embed = discord.Embed(
                    title="<:Cross:1490727525356278064> Lack of Permissions",
                    description="You need the **Auth Manager** role to remove auth roles.",
                    color=discord.Color.red()
                )
            else:
                embed = discord.Embed(
                    title="<:Cross:1490727525356278064> Lack of Permissions",
                    description="You do not have permission to remove this role.",
                    color=discord.Color.red()
                )
            return await ctx.send(embed=embed, ephemeral=True)

        try:
            if role in user.roles:
                await user.remove_roles(role, reason=f"Persisted role removed by {ctx.author} ({ctx.author.id})")

            # Remove from persisted roles in database
            self.remove_from_persisted(user.id, role.id)

            self.log_to_db(user.id, role.id, role.name, "persist_remove", ctx.author.id)

            embed = discord.Embed(
                title="✅ Persisted Role Removed",
                description=f"**User:** {user.mention} (`{user.id}`)\n**Role:** {role.mention} (`{role.name}` | `{role.id}`)\n**Removed by:** {ctx.author.mention}\n**Time:** {self.get_timestamp()}\n**Persisted:** ❌ This role will NOT be restored if they rejoin",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to remove that role.", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {e}", ephemeral=True)

    # ============================================================
    # NOTE SYSTEM
    # ============================================================

    @commands.hybrid_command(name="note", description="Adds a note to a user (AAT Staff only)")
    async def note(self, ctx: commands.Context, user: discord.Member, *, note_text: str):
        """Adds a note to a user in the database"""
        if not self.is_admin(ctx):
            return await ctx.send("You do not have permission to use this command.", ephemeral=True)

        from utils.databases import notes_db

        info = notes_db.find_one({"user_id": user.id})
        note_data = {
            "note": note_text,
            "moderator_id": ctx.author.id,
            "timestamp": self.get_timestamp()
        }

        if info:
            notes_db.update_one({"user_id": user.id}, {"$push": {"notes": note_data}})
        else:
            notes_db.insert_one({"user_id": user.id, "notes": [note_data]})

        embed = discord.Embed(
            title="<:Check:1490727471761457335> Note Added",
            description=f"**User:** {user.mention} (`{user.id}`)\n**Note:** {note_text}\n**Added by:** {ctx.author.mention}\n**Time:** {self.get_timestamp()}",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="mynotes", description="View your notes")
    async def mynotes(self, ctx: commands.Context):
        """View your notes from the database"""
        from utils.databases import notes_db

        info = notes_db.find_one({"user_id": ctx.author.id})
        if not info or not info.get("notes"):
            embed = discord.Embed(
                title="<:Cross:1490727525356278064> No Notes",
                description="You don't have any notes.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed, ephemeral=True)

        notes = info["notes"]
        embed = discord.Embed(
            title="📝 Your Notes",
            description=f"**User:** {ctx.author.mention} (`{ctx.author.id}`)\n**Total Notes:** {len(notes)}",
            color=discord.Color.blue()
        )
        for i, note in enumerate(notes, 1):
            embed.add_field(
                name=f"Note #{i}",
                value=f"**Note:** {note.get('note', 'N/A')}\n**By:** <@{note.get('moderator_id', 0)}>\n**Time:** {note.get('timestamp', 'N/A')}",
                inline=False
            )
        await ctx.send(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(ReactionRoles(bot))
