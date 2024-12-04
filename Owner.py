import discord
import discordlists
import asyncio
import btime
from discord.ext import commands
from discord.ext.commands import Paginator
from discord.ext import commands, tasks
from discord.utils import escape_markdown, find

class owner(commands.Cog, name="owner"):

    def __init__(self, bot):
        self.bot = bot
        self.help_icon = "<:owner:784461000463089714>"
        self.big_icon = "https://cdn.discordapp.com/emojis/784461000463089714.png?v=1"
        self._last_result = None
        self.api = discordlists.Client(self.bot)  # Create a Client instance
        self.api.start_loop()
        self.color = discord.Colour.from_rgb(250,0,0)

    @commands.command()
    @commands.is_owner()
    async def list_servers(self, ctx, page: int = 1):
        """> List all servers the bot is in with pagination using reactions."""
        # Fetch the bot's guilds
        guilds = self.bot.guilds

        # Set the number of servers to show per page
        servers_per_page = 1
        total_pages = (len(guilds) // servers_per_page) + (1 if len(guilds) % servers_per_page > 0 else 0)

        # Ensure the page number is valid
        if page < 1 or page > total_pages:
            embed = discord.Embed(
                title="Invalid Page",
                description=f"Please enter a page number between 1 and {total_pages}.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Calculate the start and end index for the guilds list based on the page number
        start = (page - 1) * servers_per_page
        end = start + servers_per_page
        guilds_on_page = guilds[start:end]

        # Prepare the list of servers and their invite links
        server_list = ""
        for guild in guilds_on_page:
            invite_link = "No invite available"
            try:
                if guild.text_channels:
                    invite = await guild.text_channels[0].create_invite(max_age=0, max_uses=0, unique=False)
                    invite_link = invite.url
            except Exception:
                invite_link = "Invite creation failed"

            server_list += f"**{guild.name}** (`{guild.id}`)\nInvite: {invite_link}\n\n"

        # Create the embed to display the list of servers
        embed = discord.Embed(
            title=f"Bot's Servers - Page {page}/{total_pages}",
            description=server_list or "No servers available.",
            color=discord.Color.blue()
        )

        # Send the embed and add the reactions
        message = await ctx.send(embed=embed)
        await message.add_reaction("◀️")  # Previous page
        await message.add_reaction("▶️")  # Next page

        # Define a check for the reactions
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"] and reaction.message.id == message.id

        # Wait for the user's reaction
        while True:
            try:
                reaction, user = await ctx.bot.wait_for("reaction_add", timeout=60.0, check=check)

                if str(reaction.emoji) == "◀️" and page > 1:
                    page -= 1
                elif str(reaction.emoji) == "▶️" and page < total_pages:
                    page += 1
                else:
                    continue

                # Update the start and end indexes for the new page
                start = (page - 1) * servers_per_page
                end = start + servers_per_page
                guilds_on_page = guilds[start:end]

                # Update the server list for the new page
                server_list = ""
                for guild in guilds_on_page:
                    invite_link = "No invite available"
                    try:
                        if guild.text_channels:
                            invite = await guild.text_channels[0].create_invite(max_age=0, max_uses=0, unique=False)
                            invite_link = invite.url
                    except Exception:
                        invite_link = "Invite creation failed"

                    server_list += f"**{guild.name}** (`{guild.id}`)\nInvite: {invite_link}\n\n"

                # Update the embed with the new page
                embed = discord.Embed(
                    title=f"Bot's Servers - Page {page}/{total_pages}",
                    description=server_list or "No servers available.",
                    color=discord.Color.blue()
                )
                await message.edit(embed=embed)
                await message.remove_reaction(reaction, user)  # Remove the user's reaction to prevent spamming

            except Exception:
                # Break the loop if the user doesn't react within the timeout
                break

        # Clear all reactions after pagination ends
        await message.clear_reactions()

    @commands.command(hidden=True)
    @commands.is_owner()
    async def o_dm(self, ctx, user: discord.User, *, msg=None):
        """> DM a user"""
        if user != None and msg != None:
            try:
                msg = msg or "This Message is sent via DM"
                await user.send(msg)
                await ctx.send(f"`{msg}` sent to {user.name}: {ctx.author.name}")
            except:
                await ctx.channel.send("Couldn't dm the given user.")
        else:
            await ctx.channel.send("You didn't provide a user's id and/or a message.")

    @commands.command()
    @commands.is_owner()
    async def list_users(self, ctx, page: int = 1):
        """> List all users in the server with pagination using reactions."""

        # Get the list of members in the server
        members = ctx.guild.members

        # Set the number of users to show per page
        users_per_page = 2
        total_pages = (len(members) // users_per_page) + (1 if len(members) % users_per_page > 0 else 0)

        # Ensure the page number is valid
        if page < 1 or page > total_pages:
            embed = discord.Embed(
                title="Invalid Page",
                description=f"Please enter a page number between 1 and {total_pages}.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Calculate the start and end index for the members list based on the page number
        start = (page - 1) * users_per_page
        end = start + users_per_page
        users_on_page = members[start:end]

        # Create the paginated list of users
        user_list = "\n".join([f"{member.name}#{member.discriminator}" for member in users_on_page])

        # Create the embed to display the list of users
        embed = discord.Embed(
            title=f"Users in {ctx.guild.name}",
            description=f"**Page {page}/{total_pages}**\n{user_list}",
            color=discord.Color.blue()
        )

        # Send the embed and add the reactions
        message = await ctx.send(embed=embed)
        await message.add_reaction("◀️")  # Previous page
        await message.add_reaction("▶️")  # Next page

        # Define a check for the reactions
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"] and reaction.message.id == message.id

        # Wait for the user's reaction
        while True:
            try:
                reaction, user = await ctx.bot.wait_for("reaction_add", timeout=60.0, check=check)

                if str(reaction.emoji) == "◀️" and page > 1:
                    page -= 1
                    start = (page - 1) * users_per_page
                    end = start + users_per_page
                    users_on_page = members[start:end]
                    user_list = "\n".join([f"{member.name}#{member.discriminator}" for member in users_on_page])

                    embed = discord.Embed(
                        title=f"Users in {ctx.guild.name}",
                        description=f"**Page {page}/{total_pages}**\n{user_list}",
                        color=discord.Color.blue()
                    )
                    await message.edit(embed=embed)
                    await message.remove_reaction(reaction, user)  # Remove user's reaction to prevent spamming
                elif str(reaction.emoji) == "▶️" and page < total_pages:
                    page += 1
                    start = (page - 1) * users_per_page
                    end = start + users_per_page
                    users_on_page = members[start:end]
                    user_list = "\n".join([f"{member.name}#{member.discriminator}" for member in users_on_page])

                    embed = discord.Embed(
                        title=f"Users in {ctx.guild.name}",
                        description=f"**Page {page}/{total_pages}**\n{user_list}",
                        color=discord.Color.blue()
                    )
                    await message.edit(embed=embed)
                    await message.remove_reaction(reaction, user)  # Remove user's reaction to prevent spamming

            except Exception as e:
                # If the user doesn't react or there is an error, stop the loop
                break
        
        # Remove all reactions after the pagination finishes
        await message.clear_reactions()

    @commands.command(hidden=True)
    @commands.is_owner()
    async def join(self, ctx):
        """> Summons the bot to your voice channel"""
        await ctx.author.voice.channel.connect() #Joins author's voice channel

    @commands.command(hidden=True)
    @commands.is_owner()
    async def leave(self, ctx):
        """> Disconnect the bot from the voice channel"""
        await ctx.voice_client.disconnect()

    @commands.command()
    @commands.is_owner()
    async def invite(self, ctx):
        """> Invite bot to your server"""
        embed = discord.Embed(colour=discord.Colour.from_rgb(250, 0, 0),
                              description=f"<:DarkNemesis:770563343974400010> You can invite me by clicking \
                              [here](https://discord.com/api/oauth2/authorize?client_id=785775388286517249&permissions=8&scope=bot)")
        await ctx.send(embed=embed)


    @commands.group(hidden=True)
    @commands.is_owner()
    async def change(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(str(ctx.command))

    @change.command(name="username", hidden=True)
    @commands.is_owner()
    async def change_username(self, ctx, *, name: str):
        """> Change username. """
        try:
            await self.bot.user.edit(username=name)
            await ctx.send(f"Successfully changed username to **{name}**")
        except discord.HTTPException as err:
            await ctx.send(err)

    @change.command(name="nickname", hidden=True)
    @commands.is_owner()
    async def change_nickname(self, ctx, *, name: str = None):
        """> Change nickname. """
        try:
            await ctx.guild.me.edit(nick=name)
            if name:
                await ctx.send(f"Successfully changed nickname to **{name}**")
            else:
                await ctx.send("Successfully removed nickname")
        except Exception as err:
            await ctx.send(err)

async def setup(bot):
    await bot.add_cog(owner(bot))
