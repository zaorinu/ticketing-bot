# Ticketing Bot for Discord

This project is a Discord bot designed to manage a private ticketing system using threads. It supports opening and closing tickets, saving chat transcripts, and automatic cog reloading during development.

## Features

* Open private support tickets via thread creation.
* Close tickets with reason input via modal.
* Save ticket transcripts as text files and send them to a log channel.
* Detect changes in cog files (`ticket` and `transcript`) and automatically reload them without restarting the bot.
* Slash commands for ticket panel and transcript generation.

## Project Structure

```
.
├── .env                        # Environment variables
├── bot.py                      # Bot main entry point and cog reloader
├── cogs
│   ├── ticket.py               # Ticket management cog
│   └── transcript.py           # Transcript management cog
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Setup

1. Create a `.env` file with the following variables:

```env
DISCORD_TOKEN=your_discord_bot_token
GUILD_ID=your_guild_id
STAFF_ROLE_ID=staff_role_id_for_ticket_notifications
TRANSCRIPT_CHANNEL_ID=channel_id_for_ticket_transcripts
TICKET_CHANNEL_ID=channel_id_where_threads_are_created
TICKET_ROLE_ID=role_id_assigned_when_ticket_is_open
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the bot:

```bash
python bot.py
```

The bot will watch for changes in the `cogs/` directory and reload changed cogs automatically.

## Usage

* Use the `/panel` command to post the ticket panel with a button to open tickets.
* When a user clicks "Open Ticket", a private thread will be created for them.
* Inside the ticket thread, users can use buttons to close the ticket or save the transcript.
* Closing a ticket generates a transcript, sends it to the log channel, and archives the thread.
* The `/transcript` command can also be used inside a thread to save the transcript to the log channel.

## Technical Details

* Uses `discord.py` with command tree (slash commands).
* Ticket threads are named by the user ID for identification.
* Transcript files are temporarily saved locally and sent before deletion.
* File watching is implemented using `watchdog` to reload cogs live during development.
* Environment variables handle all sensitive data and configuration IDs.
