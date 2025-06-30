import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import os

class TicketButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label="Open Ticket", custom_id="open_ticket", style=discord.ButtonStyle.primary))

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

class TicketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_id = int(os.getenv("GUILD_ID"))
        self.staff_role_id = int(os.getenv("STAFF_ROLE_ID"))
        self.transcript_channel_id = int(os.getenv("TRANSCRIPT_CHANNEL_ID"))
        self.ticket_channel_id = int(os.getenv("TICKET_CHANNEL_ID"))

    async def has_open_ticket(self, guild: discord.Guild, user_id: int) -> bool:
        channel = guild.get_channel(self.ticket_channel_id)
        if not channel:
            return False

        threads = channel.threads
        return any(thread.name == str(user_id) for thread in threads)

    @app_commands.command(name="panel", description="Send the ticket panel")
    async def panel(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Support",
            description="Click the button below to open a private support ticket.",
            color=0x2b2d31
        )
        await interaction.response.send_message(embed=embed, view=TicketButtons(), ephemeral=False)

    async def create_ticket(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        member = interaction.user

        if await self.has_open_ticket(guild, member.id):
            await interaction.followup.send("You already have an open ticket.", ephemeral=True)
            return

        ticket_channel = guild.get_channel(self.ticket_channel_id)
        if not ticket_channel:
            await interaction.followup.send("Ticket channel not found.", ephemeral=True)
            return

        thread = await ticket_channel.create_thread(
            name=str(member.id),
            type=discord.ChannelType.private_thread,
            invitable=False
        )
        await thread.add_user(member)

        staff_role = guild.get_role(self.staff_role_id)
        if staff_role:
            for m in staff_role.members:
                await thread.add_user(m)

        await thread.send(
            f"{member.mention}, your ticket has been opened. A team member will assist you shortly.",
            view=TicketActions(self)
        )

        await interaction.followup.send(f"Ticket created: {thread.mention}", ephemeral=True)

    async def close_ticket(self, interaction: discord.Interaction, reason: str):
        if not isinstance(interaction.channel, discord.Thread):
            await interaction.response.send_message("This command can only be used inside a ticket thread.", ephemeral=True)
            return

        try:
            user_id = int(interaction.channel.name.strip())
            author_member = interaction.guild.get_member(user_id)
        except:
            await interaction.response.send_message("Could not identify the ticket author.", ephemeral=True)
            return

        messages = [msg async for msg in interaction.channel.history(oldest_first=True, limit=100)]
        log_lines = []
        for msg in messages:
            ts = msg.created_at.strftime("%Y-%m-%d %H:%M")
            log_lines.append(f"[{ts}] {msg.author.display_name} ({msg.author.name}): {msg.content}")

        log_lines += [
            "\n---",
            f"Closed by: {interaction.user} ({interaction.user.id})",
            f"Reason: {reason}",
            f"Opened at: {interaction.channel.created_at.strftime('%Y-%m-%d %H:%M')}",
            f"Closed at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
        ]

        transcript_text = "\n".join(log_lines)
        file_name = f"transcript-{interaction.channel.name}.txt"
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(transcript_text)

        log_channel = interaction.guild.get_channel(self.transcript_channel_id)
        if log_channel:
            await log_channel.send(
                content=f"Transcript from {interaction.channel.mention} closed by {interaction.user.mention}",
                file=discord.File(file_name)
            )

        try:
            await author_member.send(
                content=f"Here is the transcript of your ticket: `{interaction.channel.name}`",
                file=discord.File(file_name)
            )
        except:
            pass

        os.remove(file_name)

        await interaction.channel.edit(name=f"closed-{interaction.channel.name}")
        await interaction.channel.send("This ticket has been closed.")
        await interaction.channel.edit(archived=True, locked=True)

    async def send_transcript(self, interaction: discord.Interaction, manual=False):
        messages = [msg async for msg in interaction.channel.history(oldest_first=True, limit=100)]
        log_lines = []
        for msg in messages:
            ts = msg.created_at.strftime("%Y-%m-%d %H:%M")
            log_lines.append(f"[{ts}] {msg.author.display_name} ({msg.author.name}): {msg.content}")

        if manual:
            log_lines += [
                "\n---",
                f"Requested by: {interaction.user} ({interaction.user.id})",
                f"Requested at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
            ]

        transcript_text = "\n".join(log_lines)
        file_name = f"transcript-{interaction.channel.name}.txt"
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(transcript_text)

        await interaction.followup.send("Transcript saved:", file=discord.File(file_name), ephemeral=True)
        os.remove(file_name)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type == discord.InteractionType.component and interaction.data.get("custom_id") == "open_ticket":
            await self.create_ticket(interaction)

    async def cog_load(self):
        guild = discord.Object(id=self.guild_id)
        self.bot.tree.add_command(self.panel, guild=guild)

async def setup(bot):
    cog = TicketCog(bot)
    await bot.add_cog(cog)
    bot.add_view(TicketButtons())
    bot.add_view(TicketActions(cog))
