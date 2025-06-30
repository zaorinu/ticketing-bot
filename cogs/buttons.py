import discord

class TicketButtons(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(label="Open Ticket", custom_id="open_ticket", style=discord.ButtonStyle.primary)
    async def open_ticket_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.cog.create_ticket(interaction)

class CloseTicketModal(discord.ui.Modal, title="Close Ticket"):
    reason = discord.ui.TextInput(
        label="Reason",
        placeholder="Why are you closing this ticket?",
        style=discord.TextStyle.paragraph,
        required=True
    )

    def __init__(self, cog, interaction: discord.Interaction):
        super().__init__()
        self.cog = cog
        self.interaction = interaction

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("Closing ticket...", ephemeral=True)
        await self.cog.close_ticket(self.interaction, self.reason.value)

class TicketActions(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(label="Close", style=discord.ButtonStyle.danger, custom_id="close_ticket")
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CloseTicketModal(self.cog, interaction))

    @discord.ui.button(label="Save", style=discord.ButtonStyle.secondary, custom_id="save_transcript")
    async def transcript_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await self.cog.send_transcript(interaction, manual=True)

async def setup(bot):
    pass
