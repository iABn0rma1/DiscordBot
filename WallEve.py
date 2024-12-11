import time
import datetime

from datetime import datetime
from zoneinfo import ZoneInfo

from io import BytesIO
from PIL import Image, ImageDraw

import json
import asyncio
import aiohttp

import discord
import DiscordUtils
from discord.ext import commands, tasks

import os

client = commands.Bot(command_prefix=commands.when_mentioned_or('%'), intents=discord.Intents.all(),
                      description="BOT", pm_help=True, case_insensitive=True,
                      owner_id=os.environ.get("DISCORD_BOT_OWNER_ID")
                      )
tracker = DiscordUtils.InviteTracker(client)

client._uptime = None
client.remove_command("help")

EXTENSIONS = [
    "Admin",
    "Fun",
    "Games",
    # "Giveaway",
    "Configure",
    "Help",
    "Miscellaneous",
    "Moderation",
    "Owner",
    # "tickets", 
    "Utility",
]

@client.event
async def on_connect():
    if client._uptime is None:
        print(f"Connected to Discord. Getting ready...")
        print(f'-----------------------------')

@client.event
async def on_ready():
    change_status.start()
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('--------------------------------------')
    client.starttime = time.time()
    print(client.starttime)
    print(f'--------------------------------------')
    print(f'Bot ready!')
    print(f"Successfully logged in as: {client.user.name}")
    print(f"ID: {client.user.id}")
    print(f"Total servers: {len(client.guilds)}")
    print(f"Total Members: {len(client.users)}")
    print(f"Discord.py version: {discord.__version__}")
    print(f'--------------------------------------')
    await tracker.cache_invites()
    for extension in EXTENSIONS:
        try:
            await client.load_extension(extension)
        except Exception as e:
            print(e)

@tasks.loop(seconds=10)
async def change_status():
    await client.change_presence(activity=discord.Game(name="%help"), 
                                 status=discord.Status.idle)
    await asyncio.sleep(10)
    await client.change_presence(activity=discord.Activity
                                 (type=discord.ActivityType.listening, name="DM for help"),
                                 status=discord.Status.idle)
    await asyncio.sleep(10)

@client.event
async def on_member_join(member):
    # Load config.json to fetch the guild and welcome channel ID
    with open('config.json', 'r') as f:
        config_data = json.load(f)

    guild_id = str(member.guild.id)  # Convert guild ID to string
    if guild_id not in config_data:
        print("Guild not found in config.")
        return

    # Fetch welcome channel ID from config
    welcome_channel_id = config_data[guild_id].get('important_channels', {}).get('welcome', None)
    if not welcome_channel_id:
        print("Welcome channel not set in config.")
        return

    # Load the welcome image and process the avatar
    welcome = Image.open("welcome.png")
    AVATAR_SIZE = 256

    # Fetch the avatar image
    async with aiohttp.ClientSession() as session:
        async with session.get(member.avatar.url) as response:
            if response.status != 200:
                print("Failed to fetch avatar image.")
                return
            avatar_data = BytesIO(await response.read())

    # Process the avatar image
    avatar_image = Image.open(avatar_data).convert("RGBA")
    avatar_image = avatar_image.resize((AVATAR_SIZE, AVATAR_SIZE))

    # Create a circular mask for the avatar
    circle_image = Image.new("L", (AVATAR_SIZE, AVATAR_SIZE), 0)
    circle_draw = ImageDraw.Draw(circle_image)
    circle_draw.ellipse((0, 0, AVATAR_SIZE, AVATAR_SIZE), fill=255)

    # Apply the circular mask
    circular_avatar = Image.new("RGBA", (AVATAR_SIZE, AVATAR_SIZE))
    circular_avatar.paste(avatar_image, (0, 0), mask=circle_image)

    # Paste the circular avatar onto the welcome image
    welcome.paste(circular_avatar, (460, 45), circular_avatar)

    # Save the final image to a BytesIO object
    output = BytesIO()
    welcome.save(output, format="PNG")
    output.seek(0)  # Reset stream position

    # Fetch the inviter (this assumes you have a `tracker` object set up to fetch the inviter)
    inviter = await tracker.fetch_inviter(member)

    # Create the embed message
    embed = discord.Embed(
        color=discord.Color.from_rgb(250, 0, 0),
        description=f"<a:DN_Wlcm:720229315723132950> Welcome to {member.guild.name},\
                      where nemesis thrives and the weak die.\
                      \n<a:DN_ThisR:719866047930302464> Be sure to read <#{config_data[guild_id].get('important_channels', {}).get('rules', 'Not set')}>\
                      \n<a:DN_ThisR:719866047930302464> and claim your roles from <#{config_data[guild_id].get('important_channels', {}).get('roles', 'Not set')}>"
    )
    embed.set_author(
        name=f"Namaste {member.name}",
        icon_url=member.avatar.url
    )

    # Set the footer with inviter info and total member count
    embed.set_footer(text=f"Invited by: {inviter} | Total Members: {len(list(member.guild.members))}")

    # Get the channel where the welcome message should be sent
    welcome_channel = client.get_channel(int(welcome_channel_id))

    if welcome_channel:
        # Send the embed with the in-memory image
        file = discord.File(output, filename="welcome.png")
        embed.set_image(url="attachment://welcome.png")
        await welcome_channel.send(file=file, embed=embed)
    else:
        print(f"Welcome channel with ID {welcome_channel_id} not found in guild.")

@client.event
async def on_message(message):
    # Avoid responding to bot's own messages
    if message.author == client.user:
        return

    # Handle messages mentioning the bot for prefix information
    if message.content.startswith(f"<@!{client.user.id}>") or message.content == f"<@!{client.user.id}>":
        await message.channel.send(f"My prefix is `%`")
        return

    # Load configuration data from JSON
    with open('config.json', 'r') as f:
        config_data = json.load(f)

    # Determine the context: Guild or DM
    if isinstance(message.channel, discord.DMChannel):
        # Handle direct messages (mod mail)
        await handle_direct_message(client, message, config_data)
    else:
        # Handle guild-specific events
        guild_id = str(message.guild.id)
        
        # React to messages in the meme channel
        meme_channel_id = config_data.get(guild_id, {}).get('important_channels', {}).get('memes')
        if meme_channel_id and message.channel.id == int(meme_channel_id):
            await message.add_reaction("<:PizzaSlut:1217203161429708873>")
        
        # Fetch the logs channel
        log_channel_id = config_data.get(guild_id, {}).get('important_channels', {}).get('logs')
        if log_channel_id:
            client.channel = client.get_channel(int(log_channel_id))
            if not client.channel:
                print(f'Log channel with ID {log_channel_id} not found.')

    # Allow commands to be processed by commands extension
    await client.process_commands(message)

async def handle_direct_message(client, message, config_data):
    """Handles incoming direct messages."""
    author = message.author

    # Attempt to find the author in the client's guilds to resolve nickname
    for guild in client.guilds:
        member = guild.get_member(author.id)
        if member:
            author = member
            break

    # Create the embed for the mod mail
    embed = discord.Embed(
        title="Mod Mail 📬",
        description=message.content,
        colour=discord.Colour.from_rgb(250, 0, 0),
        timestamp=datetime.now(ZoneInfo("Asia/Kolkata")),
    )
    author_name = f"{author.nick} ({author})" if isinstance(author, discord.Member) and author.nick else str(author)
    embed.set_author(name=author_name)

    # Handle attachments if any
    if message.attachments:
        attachment_urls = [
            f"[{attachment.filename}]({attachment.url}) ({attachment.size} bytes)"
            for attachment in message.attachments
        ]
        embed.add_field(name="Attachments", value="\n".join(attachment_urls), inline=False)

    # Send the mod mail to the log channel
    to_send = f"{author.mention}"
    if hasattr(client, 'channel') and client.channel:
        await client.channel.send(to_send, embed=embed)
        client.last_id = author.id
    else:
        print("Log channel not set. Ensure the log channel is configured properly.")
