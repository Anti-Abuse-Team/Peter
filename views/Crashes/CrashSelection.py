import discord
from discord import ui
from discord.ui import View, Select

class CrashDropdown(discord.ui.Select):
    def __init__(self, user_roles, ctx):
        self.ctx = ctx

        options = []
        for i, role_id in enumerate(user_roles):
            role = ctx.guild.get_role(role_id)
            if role:
                options.append(
                    discord.SelectOption(
                        label=f"{i+1}. {role.name}",
                        value=str(role.id) 
                    )
                )

        if not options:
            options.append(
                discord.SelectOption(label="No valid roles", value="none")
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

        if self.values[0] == "none":
            await interaction.response.send_message("No roles available.", ephemeral=True)
            return
        
        self.view.selected_role_id = int(self.values[0])
        await interaction.response.defer()
        self.view.stop()

class CrashSelection(ui.LayoutView):
    def __init__(self, roles, ctx):
        super().__init__()

        container = ui.Container(
            ui.TextDisplay("### Role Selection"),
            ui.Separator(),
            ui.TextDisplay("Please select one of the following roles to modify;"),
        )

        row = ui.ActionRow(CrashDropdown(roles, ctx))
        container.add_item(row)
        self.add_item(container)