import discord
from discord import ui

class PingDropdown(ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Announcement Ping", value=1374412126705422347, emoji="<:Announcement:1492362977410547812>"),
            discord.SelectOption(label="Dead Chat Ping", value=1291869585867276308, emoji="<:Dead:1492362975170924615>"),
            discord.SelectOption(label="Question of the Day Ping", value=1293767506691096636, emoji="<:Question:1492362973023309835>"),
            discord.SelectOption(label="Giveaway Ping", value=1355230077503410288, emoji="<:Giveaway:1492362970959712357>"),
            discord.SelectOption(label="Witch Hunter Ping", value=1322890862551629897, emoji="<:Witch:1492362969177133167>")
        ]

        super().__init__(
            placeholder="Choose an option...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        id = self.values[0]

        role = interaction.guild.get_role(int(id))
        if role is None:
            await interaction.followup.send("Failed to locate role.", ephemeral=True)
            return

        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.followup.send(f"Removed role **{role.name}**", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.followup.send(f"Added role **{role.name}**", ephemeral=True)


class PingReactionRoles(ui.LayoutView):
    def __init__(self):
        super().__init__(timeout=None)

        container = ui.Container(
            ui.TextDisplay("### Ping Roles"),
            ui.Separator(),
            ui.TextDisplay("These are the following roles you can get pings for;\n> <:Announcement:1492362977410547812>  |  Dead Chat Ping\n> <:Dead:1492362975170924615>  | Question of The Day Ping\n> <:Question:1492362973023309835>  |  Giveaway Ping\n> <:Giveaway:1492362970959712357>  |  Announcements Ping\n> <:Witch:1492362969177133167>  |  Witch Hunter Ping\n"),
            ui.Separator()
        )

        container.accent_color = 0x00e586
        row = ui.ActionRow(PingDropdown())
        container.add_item(row)

        self.add_item(container)

class ColorDropdown(ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Red", value=1272610308787146752, emoji="<:Red:1492362983035109466>"),
            discord.SelectOption(label="Orange", value=1272610324020727808, emoji="<:Orange:1492365963507531836>"),
            discord.SelectOption(label="Yellow", value=1272610334078926868, emoji="<:Yellow:1492362987162308638>"),
            discord.SelectOption(label="Green", value=1272610346586083484, emoji="<:Green:1492365965294436512>"),
            discord.SelectOption(label="Cyan", value=1272610860300374016, emoji="<:Cyan:1492365966699397302>"),
            discord.SelectOption(label="Blue", value=1272610361035722875, emoji="<:Blue:1492365968301621398>"),
            discord.SelectOption(label="Purple", value=1272610862456377527, emoji="<:Purple:1492365937855434924>"),
            discord.SelectOption(label="Pink", value=1272610863626584084, emoji="<:Pink:1492365939671437415>"),
            discord.SelectOption(label="Brown", value=1314104883674218506, emoji="<:Brown:1492365944889147403>"),
            discord.SelectOption(label="White", value=1273428840814870528, emoji="<:White:1492365941323989172>"),
            discord.SelectOption(label="Black", value=1273429025083101305, emoji="<:Black:1492365942833942722>")
        ]

        super().__init__(
            placeholder="Choose an option...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        id = self.values[0]

        role = interaction.guild.get_role(int(id))
        if role is None:
            await interaction.followup.send("Failed to locate role.", ephemeral=True)
            return

        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.followup.send(f"Removed role **{role.name}**", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.followup.send(f"Added role **{role.name}**", ephemeral=True)
        
        

class ColorReactionRoles(ui.LayoutView):
    def __init__(self):
        super().__init__(timeout=None)

        container = ui.Container(
            ui.TextDisplay("### Color Roles"),
            ui.Separator(),
            ui.TextDisplay("These are the following roles you can have for colors;\n> <:Red:1492362983035109466>  |  Red\n> <:Orange:1492365963507531836>  |  Orange\n> <:Yellow:1492362987162308638>  | Yellow\n> <:Green:1492365965294436512>  |  Green\n> <:Cyan:1492365966699397302>  |  Cyan\n> <:Blue:1492365968301621398>  |  Blue\n> <:Purple:1492365937855434924>  |  Purple\n> <:Pink:1492365939671437415>  |  Pink\n> <:Brown:1492365944889147403>  |  Brown\n> <:White:1492365941323989172>  |  White\n> <:Black:1492365942833942722>  |  Black"),
            ui.Separator()
        )

        container.accent_color = 0x00e586
        row = ui.ActionRow(ColorDropdown())
        container.add_item(row)

        self.add_item(container)


class LeaveDropdown(ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Leave of Absence", value=1292814355921899603, emoji="<:Leave:1492365946688639148>"),
            discord.SelectOption(label="Retired", value=1272725411603808367, emoji="<:Retired:1492365948600979647>")
        ]

        super().__init__(
            placeholder="Choose an option...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        id = self.values[0]

        role = interaction.guild.get_role(int(id))
        if role is None:
            await interaction.followup.send("Failed to locate role.", ephemeral=True)
            return

        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.followup.send(f"Removed role **{role.name}**", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.followup.send(f"Added role **{role.name}**", ephemeral=True)

class LeaveReactionRoles(ui.LayoutView):
    def __init__(self):
        super().__init__(timeout=None)

        container = ui.Container(
            ui.TextDisplay("### Leave Roles"),
            ui.Separator(),
            ui.TextDisplay("These are the following roles you can choose for leaving;\n> <:Leave:1492365946688639148>  |  Leave of Absence\n > <:Retired:1492365948600979647>  |  Retired"),
            ui.Separator()
        )

        container.accent_color = 0x00e586
        row = ui.ActionRow(LeaveDropdown())
        container.add_item(row)

        self.add_item(container)
