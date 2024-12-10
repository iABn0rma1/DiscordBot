import os
import discord
from discord.ext import commands
import json
from discord.utils import get

# Load configuration data from tickets.json
def load_ticket_config():
    with open('tickets.json', 'r') as file:
        data = json.load(file)
    return data

# Save configuration data to tickets.json
def save_ticket_config(data):
    with open('tickets.json', 'w') as file:
        json.dump(data, file, indent=4)

# Ticket system Cog
class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ticket_config = self.load_ticket_config()  # Load the ticket configuration


    # Load configuration data from tickets.json, handle if file is missing or empty
    async def load_ticket_config(self, ):
        file_path = 'tickets.json'
        if not os.path.exists(file_path):
            # If file doesn't exist, initialize it with default data
            save_ticket_config({})
            return {}

        with open(file_path, 'r') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                # If JSON is invalid or empty, return an empty dictionary and initialize it
                save_ticket_config({})
                return {}

        return data

    # Save configuration data to tickets.json
    async def save_ticket_config(self, data):
        with open('tickets.json', 'w') as file:
            json.dump(data, file, indent=4)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Handles reactions added to messages in the ticket system."""
        
        # Check if the reaction is from the correct guild
        if payload.guild_id != self.ticket_config['GUILD_ID']:
            return

        # Fetch the guild and channel
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return  # If the guild is not found, return

        channel = guild.get_channel(payload.channel_id)
        if not channel:
            return  # If the channel is not found, return

        # Fetch the message where the reaction was added
        message = await channel.fetch_message(payload.message_id)
        if message.author != self.bot.user:
            return  # Ignore messages that are not sent by the bot

        # Handle different reaction emojis and open tickets accordingly
        if payload.emoji.name == '❓':
            await self.open_ticket(payload.user_id, "General Question", channel)
        elif payload.emoji.name == '<:privacy:733465503594708992>':
            await self.open_ticket(payload.user_id, "Privacy Policy", channel)
        elif payload.emoji.name == '<:partner:748833273383485440>':
            await self.open_ticket(payload.user_id, "Partnership", channel)
        elif payload.emoji.name == '🐛':
            await self.open_ticket(payload.user_id, "Bug Report", channel)

    async def open_ticket(self, user_id, issue_type, channel):
        """Open a new ticket for the user."""
        guild = channel.guild
        member = guild.get_member(user_id)
        
        if not member:
            return

        # Create a new ticket category if it doesn't exist
        category = discord.utils.get(guild.categories, name="Tickets")
        if not category:
            category = await guild.create_category("Tickets")

        # Create a ticket text channel
        ticket_channel = await guild.create_text_channel(f"ticket-{user_id}", category=category)

        # Set the permissions for the ticket channel
        await ticket_channel.set_permissions(guild.default_role, read_messages=False)
        await ticket_channel.set_permissions(member, read_messages=True, send_messages=True)

        # Send a welcome message
        await ticket_channel.send(f"Hello {member.mention}, your ticket for {issue_type} has been created.\nPlease describe your issue.")

        # Log the ticket information to tickets.json
        self.ticket_config["tickets"] = self.ticket_config.get("tickets", [])
        self.ticket_config["tickets"].append({
            "user_id": user_id,
            "issue_type": issue_type,
            "channel_id": ticket_channel.id
        })
        save_ticket_config(self.ticket_config)

    @commands.command(name='setup_ticket_system')
    @commands.has_permissions(administrator=True)
    async def setup_ticket_system(self, ctx):
        """Sets up the ticket system with a reaction-based interface."""
        
        # Send the message with reactions to open tickets
        embed = discord.Embed(title="Ticket System", description="Click a reaction below to open a ticket.")
        message = await ctx.send(embed=embed)

        # Add reactions for different ticket types
        await message.add_reaction('❓')  # General Question
        await message.add_reaction('<:privacy:733465503594708992>')  # Privacy Policy
        await message.add_reaction('<:partner:748833273383485440>')  # Partnership
        await message.add_reaction('🐛')  # Bug Report

        # Save the channel and message ID for future use
        self.ticket_config["setup_channel"] = ctx.channel.id
        self.ticket_config["setup_message"] = message.id
        save_ticket_config(self.ticket_config)

        await ctx.send("Ticket system setup is complete! Reactions have been added to the message.")

    @commands.command(name='close_ticket')
    @commands.has_permissions(manage_channels=True)
    async def close_ticket(self, ctx):
        """Closes a ticket and deletes the channel."""
        
        # Make sure this command is used in a ticket channel
        if not ctx.channel.name.startswith("ticket-"):
            await ctx.send("This command can only be used in a ticket channel.")
            return

        # Confirm closing the ticket
        await ctx.send("Are you sure you want to close this ticket? React with ✅ to confirm.")
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) == "✅" and reaction.message == ctx.message
        
        # Wait for confirmation
        try:
            await self.bot.wait_for('reaction_add', check=check, timeout=30.0)
            await ctx.send("Ticket is being closed...")
            await ctx.channel.delete()  # Delete the ticket channel
        except TimeoutError:
            await ctx.send("Ticket close operation timed out.")

# Add the cog to the bot
async def setup(bot):
    await bot.add_cog(TicketSystem(bot))
