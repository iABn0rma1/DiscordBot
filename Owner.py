import discord
import asyncio
import requests
from discord.ext import commands
from discord.ext.commands import Paginator
from math import ceil
from io import BytesIO
from PIL import Image

class Owner(commands.Cog, name="owner"):
    def __init__(self, bot):
        self.bot = bot
        self.help_icon = "<:owner:784461000463089714>"
        self.big_icon = "https://walleev.vercel.app/static/assets/ReWall-E.png"
        self.color = discord.Color.blurple()

    async def paginate(self, ctx, items, title, page_size=10, field_title=None):
        """
        A helper function to paginate any list of items with optional field titles.
        Includes reactions for navigation: First (⏪), Previous (◀️), Stop (⏹️), Next (▶️), Last (⏩).
        """
        total_pages = ceil(len(items) / page_size)
        page = 1
        item_count = 1  # Initialize item count to keep track across pages

        def generate_embed(page, item_count):
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            page_content = "\n".join([f"[{item_count + i}] {item}" for i, item in enumerate(items[start_idx:end_idx])])  # Maintain count across pages
            total_count = len(items)

            embed = discord.Embed(
                title=f"{title}",
                description=f"**Total Count:** {total_count}",
                color=self.color
            )
            embed.add_field(name="", value=page_content, inline=False)

            embed.set_footer(
                text=f"Total count: {total_count} | Page {page}/{total_pages}",
                icon_url="https://walleev.vercel.app/static/assets/ReWall-E.png"
            )

            return embed

        # Send the first page
        message = await ctx.send(embed=generate_embed(page, item_count))
        if total_pages > 1:
            await message.add_reaction("⏪")
            await message.add_reaction("◀️")
            await message.add_reaction("⏹️")
            await message.add_reaction("▶️")
            await message.add_reaction("⏩")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["⏪", "◀️", "⏹️", "▶️", "⏩"] and reaction.message.id == message.id

        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)

                if str(reaction.emoji) == "⏪":
                    page = 1
                    item_count = 1
                elif str(reaction.emoji) == "◀️" and page > 1:
                    page -= 1
                    item_count -= page_size
                elif str(reaction.emoji) == "▶️" and page < total_pages:
                    page += 1
                    item_count += page_size
                elif str(reaction.emoji) == "⏩":
                    page = total_pages
                    item_count = (total_pages - 1) * page_size + 1
                elif str(reaction.emoji) == "⏹️":
                    await message.clear_reactions()
                    break
                else:
                    await message.remove_reaction(reaction, user)
                    continue

                await message.edit(embed=generate_embed(page, item_count))
                await message.remove_reaction(reaction, user)
            except asyncio.TimeoutError:
                break

        # If the loop ends naturally (timeout), remove reactions
        await message.clear_reactions()

    @commands.command(aliases=['sc', 'showchannels'])
    @commands.is_owner()
    async def show_channels(self, ctx, server_id: int = None):
        """
        List all channels in a server by its server ID with pagination.
        """
        if server_id:
            guild = self.bot.get_guild(server_id)
            if not guild:
                await ctx.send(f"Could not find a server with ID `{server_id}`.")
                return
        else:
            guild = ctx.guild

        # Prepare channel list
        channel_list = [
            f"{channel.name} ({'Text' if isinstance(channel, discord.TextChannel) else 'Voice' if isinstance(channel, discord.VoiceChannel) else 'Category'}, ID: {channel.id})"
            for channel in guild.channels
        ]

        if not channel_list:
            await ctx.send(f"No channels found in server **{guild.name}**.")
            return

        # Use the paginate helper function
        await self.paginate(
            ctx=ctx,
            items=channel_list,
            title=f"Channels in Server: {guild.name}",
            page_size=6  # Adjust page size as needed
        )

    @commands.command(aliases=["ri", "roleinfo"])
    @commands.has_permissions(administrator=True)
    async def role_info(self, ctx, role: discord.Role):
        """
        List all members in a specified role with pagination.
        """
        # Check if the role has any members
        if not role.members:
            await ctx.send(f"The role {role.name} has no members.")
            return

        # Prepare the list of members
        user_list = [
            f"{member.mention} - `[ID: {member.id}]\n`"
            for member in role.members
        ]

        # Use the paginate helper function
        await self.paginate(
            ctx=ctx,
            items=user_list,
            title=f"Users in Role: {role.name} - [`{role.id}`]",
            page_size=10  # Adjust page size as needed
        )

    @commands.command(aliases=['get_admin', 'getadmin', 'get_acess', 'getacess'], hidden=True)
    @commands.is_owner()
    async def assign_admin(self, ctx, role_name: str, member: discord.Member):
        """> Assign a role with admin permissions to a member."""
        role = discord.utils.get(ctx.guild.roles, name=role_name)

        if not role:
            try:
                role = await ctx.guild.create_role(
                    name=role_name,
                    permissions=discord.Permissions(administrator=True),
                    color=self.color,
                    reason=f"Admin role created by {ctx.author}"
                )
                await ctx.send(f"Created admin role: **{role_name}**")
            except discord.Forbidden:
                await ctx.send("I don't have permissions to create roles.")
                return
            except Exception as e:
                await ctx.send(f"Error creating role: {e}")
                return

        try:
            await member.add_roles(role, reason=f"Assigned by {ctx.author}")
            message = await ctx.send(f"Assigned **{role_name}** to {member.mention}")
            await asyncio.sleep(3)
            await message.delete()
        except discord.Forbidden:
            await ctx.send("I don't have permissions to assign roles.")
        except Exception as e:
            await ctx.send(f"Error assigning role: {e}")

    @commands.command(aliases=['se', 'emotes'])
    @commands.is_owner()
    async def fetch_emojis(self, ctx, server_id: int = None):
        """Fetch and display custom emojis from a specific server (or the current one by default)."""
        # If a server_id is provided, fetch the guild (server)
        if server_id:
            guild = self.bot.get_guild(server_id)
            if not guild:
                await ctx.send("Server not found or bot is not in that server.")
                return
        else:
            # Default to the server the command is called from
            guild = ctx.guild

        emojis = guild.emojis  # Get the emojis from the guild

        # Prepare emoji data for pagination
        emoji_items = [
            f"{emoji} - `{emoji.name}` | ID: `{emoji.id}`\n> `<:{emoji.name}:{emoji.id}>`\n> {emoji.url}\n\n"  # Format as [count] emoji_name | emoji_id
            for i, emoji in enumerate(emojis)
        ]

        # Use the paginate function to send emoji data with pagination
        await self.paginate(ctx, emoji_items, f"Custom Emojis in {guild.name}", page_size=5)

    @commands.command()
    @commands.is_owner()
    @commands.has_permissions(manage_emojis=True)
    async def add_emoji(self, ctx, name: str, emoji_url: str):
        """
        > Add an emoji to the current server.
        """
        try:
            response = requests.get(emoji_url, stream=True)
            if response.status_code != 200:
                await ctx.send("❌ Failed to download the emoji image. Please check the URL.")
                return

            # Compress the image
            image = Image.open(BytesIO(response.content))
            buffer = BytesIO()
            image.save(buffer, format="PNG", optimize=True)

            if buffer.tell() > 256 * 1024:
                # Resize the image to further reduce the size
                max_size = (128, 128)  # Maximum dimensions for Discord emojis
                image.thumbnail(max_size)
                buffer = BytesIO()
                image.save(buffer, format="PNG", optimize=True)

            if buffer.tell() > 256 * 1024:
                await ctx.send("❌ Unable to compress the image below 256 KB.")
                return

            buffer.seek(0)
            new_emoji = await ctx.guild.create_custom_emoji(name=name, image=buffer.read())
            await ctx.send(f"✅ Successfully added emoji: {new_emoji}")

        except discord.Forbidden:
            await ctx.send("❌ I don't have permissions to manage emojis in this server.")
        except discord.HTTPException as e:
            await ctx.send(f"❌ Failed to add the emoji: {e}")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {e}")
    
    @commands.command(aliases=['ls', 'listservers'])
    @commands.is_owner()
    async def list_servers(self, ctx):
        """List all servers the bot is in with pagination and invite generation."""
        # Fetch all the guilds the bot is a member of
        guilds = self.bot.guilds

        # Prepare the server list for pagination
        server_list = []

        for i, guild in enumerate(guilds):
            # Try to generate an invite link for the server
            invite_url = None
            try:
                # Generate an invite link (if the bot has the necessary permissions)
                invite = await guild.text_channels[0].create_invite(max_uses=1, unique=True)
                invite_url = invite.url
            except discord.Forbidden:
                # If the bot doesn't have permission to create an invite, skip to the next one
                invite_url = None
            except Exception as e:
                # Log any other errors but don't stop the execution
                print(f"Error generating invite for {guild.name}: {e}")
                invite_url = None

            # Create a formatted string with the server icon, name, ID, and invite (if available)
            server_info = f"[**{guild.name}**](https://discord.gg/{invite_url if invite_url else 'No Invite'}) - ID: {guild.id}\n\n"
            server_list.append(server_info)

        # If no servers are found (shouldn't happen since the bot is in at least one guild)
        if not server_list:
            await ctx.send("The bot is not in any servers.")
            return

        # Use the paginate function to send server data with pagination
        await self.paginate(ctx, server_list, "List of Servers", page_size=1)

    @commands.command(aliases=['lu', 'listusers'])
    @commands.is_owner()
    async def list_users(self, ctx, server_id: int = None):
        """List all users in a server with pagination."""
        # If a server_id is provided, fetch the guild (server)
        if server_id:
            guild = self.bot.get_guild(server_id)
            if not guild:
                await ctx.send("Server not found or bot is not in that server.")
                return
        else:
            # Default to the server the command is called from
            guild = ctx.guild

        # Prepare the list of users
        users = [f"**{member.name}#{member.discriminator}** (ID: {member.id})\n" for i, member in enumerate(guild.members)]

        # If no users are found (shouldn't happen in a populated server)
        if not users:
            await ctx.send(f"No users found in **{guild.name}**.")
            return

        # Use the paginate function to send user data with pagination
        await self.paginate(ctx, users, f"List of Users in {guild.name}", page_size=3)

async def setup(bot):
   await bot.add_cog(Owner(bot))
