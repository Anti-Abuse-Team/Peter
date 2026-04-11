import discord
from discord.ui import View, Select

class RoleSelect(discord.ui.Select):
    def __init__(self, user_roles, ctx):
        self.ctx = ctx

        options = []
        for i, role_id in enumerate(user_roles):
            role = ctx.guild.get_role(role_id)
            if role:
                options.append(
                    discord.SelectOption(
                        label=f"{i+1}. {role.name}",
                        value=str(role_id)
                    )
                )

        if not options:
            options.append(
                discord.SelectOption(label="No valid roles", value="0", default=True)
            )

        super().__init__(
            placeholder="Select a role...",
            options=options,
            min_values=1,
            max_values=1
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(
                "You cannot use this menu!",
                ephemeral=True
            )
            return

        self.view.selected_role_id = int(self.values[0])
        await interaction.response.defer()
        self.view.stop()


class RoleSelectView(discord.ui.View):
    def __init__(self, user_roles, ctx):
        super().__init__(timeout=60)
        self.selected_role_id = None
        self.add_item(RoleSelect(user_roles, ctx))