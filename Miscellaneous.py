import requests
import discord
import random
import config
import json
import pendulum
from discord import ActivityType
from discord import Spotify, Game, Streaming, Activity, CustomActivity
from discord.ext import commands
from discord.ext.commands import BucketType
from discord.ext.commands.errors import MissingRequiredArgument, CommandOnCooldown

class Miscellaneous(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["toss", "flip"])
    @commands.guild_only()
    async def coinflip(self, ctx):
        """> Coin flip!"""
        await ctx.send(f"**{ctx.author.name}** flipped a coin and got **{random.choice(['Heads','Tails'])}**!")

    @commands.command()
    @commands.cooldown(1, 690, BucketType.user)
    async def report(self, ctx, *args):
        """> Reports to the developer"""
        if args == []:
            await ctx.send('Please give me a report to send. This has been flagged.')
            return
        counter = random.randint(1, 1000)
        channel = self.bot.get_channel(config.LOG_ID)
        x = ' '.join(map(str, args))
        if x == None:
            await ctx.send('You going to report nothing?')
        else:
            embed = discord.Embed(
                title=f'Report #{counter}',
                color=discord.Color.blue(),
                description=f'The user `{ctx.author}` from the guild `{ctx.guild}` has sent a report!'
            )
            embed.add_field(name='Query?', value=f'{x}')
            embed.set_footer(text=f'User ID: {ctx.author.id}\nGuild ID: {ctx.guild.id}')
            await channel.send(embed=embed)
            await ctx.send(f'Your report has successfully been sent!')

    @commands.command(aliases=["latency"])
    async def ping(self, ctx):
        """> See bot's latency to discord"""
        ping = round(self.bot.latency * 1000)
        await ctx.send(f":ping_pong: Pong   |   {ping}ms")

    @commands.command()
    async def status(self, ctx, user: discord.Member = None):
        """Show all activities the user is currently engaged in with full details."""
        user = user or ctx.author
        activities = user.activities

        if not activities:
            await ctx.send(f"{user.name} is not currently engaged in any activities.")
            return

        embed = discord.Embed(color=discord.Color.blurple())#, description=f"{user.display_name}'s Status")
        embed.set_footer(icon_url=user.avatar.url)

        for activity in activities:

            if hasattr(activity, 'color'):
                embed.color = activity.color

            # if activity.details:
            #     embed.add_field(name="User", value=activity.details, inline=False)

            if isinstance(activity, Game):
                embed.title = "🎮 **Playing**"
                embed.add_field(name="", value=f"> {activity.name}", inline=False)
                if activity.start:
                    embed.add_field(name="Started at:", inline=False,
                                    value=f"{discord.utils.format_dt(activity.start, style='R')} ({discord.utils.format_dt(activity.start)})")
                elif activity.end:
                    embed.add_field(name="Ended at:", value=activity.end, inline=False)
                elif activity.assets:
                    embed.add_field(name="Assets:", value=activity.assets, inline=False)
                elif activity.platform:
                    embed.add_field(name="Platform:", value=activity.platform, inline=False)
                elif activity.type:
                    embed.add_field(name="Type:", value=activity.type, inline=False)

            if activity.type == ActivityType.playing:
                embed.title = "🎮 **Playing**"
                embed.add_field(name="", value=f"> {activity.name}", inline=False)
                if activity.start:
                    embed.add_field(name="Started at:", inline=False,
                                    value=f"{discord.utils.format_dt(activity.start, style='R')} ({discord.utils.format_dt(activity.start)})")
                elif activity.end:
                    embed.add_field(name="Ended at:", value=activity.end, inline=False)
                elif activity.assets:
                    embed.add_field(name="Assets:", value=activity.assets, inline=False)
                elif activity.platform:
                    embed.add_field(name="Platform:", value=activity.platform, inline=False)
                elif activity.type:
                    embed.add_field(name="Type:", value=activity.type, inline=False)

            elif isinstance(activity, Spotify):
                embed.set_thumbnail(url=activity.album_cover_url)
                embed.title = f"🎵 {user.display_name}'s **Listening to**"
                embed.add_field(name="🎤 Song", value=f"[{activity.title}]({activity.track_url})")
                embed.add_field(name="", value="", inline=True)
                embed.add_field(name="💿 Album", value=activity.album, inline=True)
                embed.add_field(name="⏳ Duration", value=pendulum.duration(seconds=activity.duration.total_seconds()).in_words(locale="en"))
                embed.add_field(name="", value="", inline=True)
                embed.add_field(name="🔗 Spotify Link", value=f"[Click here to listen]({activity.track_url})")
                embed.add_field(name="Started at:", inline=False,
                                value=f"{discord.utils.format_dt(activity.start, style='R')} ({discord.utils.format_dt(activity.start)})")
                embed.set_footer(
                    text=f"Spotify Artist: {activity.artist}",
                    icon_url="https://cdn-icons-png.flaticon.com/512/2111/2111624.png"
                )
            elif isinstance(activity, Streaming):
                embed.title = "📡 **Streaming**"
                embed.add_field(
                    name="",
                    value=(
                        f"> **Title**:\n> {activity.name}\n\n"
                        f"> **Platform**:\n> {activity.platform}\n\n"
                        f"> **URL**:\n> [Watch here]({activity.url})"
                    ),
                    inline=False
                )
                if activity.start:
                    embed.add_field(name="Started at:", inline=False,
                                    value=f"{discord.utils.format_dt(activity.start, style='R')} ({discord.utils.format_dt(activity.start)})")
            elif isinstance(activity, CustomActivity):
                emoji = activity.emoji if activity.emoji else "None"
                embed.title = "💬 **Custom Status**"
                embed.add_field(
                    name="",
                    value=(
                        f"> **Status**:\n> {activity.name}\n\n"
                        f"> **Emoji**:\n> {emoji}"
                    ),
                    inline=False
                )
                if activity.start:
                    embed.add_field(name="Started at:", inline=False,
                                    value=f"{discord.utils.format_dt(activity.start, style='R')} ({discord.utils.format_dt(activity.start)})")
            elif activity.type == discord.ActivityType.watching:
                embed.title = "👀 **Watching**"
                embed.add_field(
                    name="",
                    value=f"> {activity.name}",
                    inline=False
                )
                if activity.start:
                    embed.add_field(name="Started at:", inline=False,
                                    value=f"{discord.utils.format_dt(activity.start, style='R')} ({discord.utils.format_dt(activity.start)})")
            elif activity.type == discord.ActivityType.listening:
                embed.title = "🎧 **Listening:**"
                embed.add_field(
                    name="",
                    value=f"> {activity.name}",
                    inline=False
                )
                if activity.start:
                    embed.add_field(name="Started at:", inline=False,
                                    value=f"{discord.utils.format_dt(activity.start, style='R')} ({discord.utils.format_dt(activity.start)})")
            elif activity.type == discord.ActivityType.competing:
                embed.title = "🏆 **Competing in**"
                embed.add_field(
                    name="",
                    value=f">> {activity.name}",
                    inline=False
                )
                if activity.start:
                    embed.add_field(name="Started at:", inline=False,
                                    value=f"{discord.utils.format_dt(activity.start, style='R')} ({discord.utils.format_dt(activity.start)})")
            elif activity.type == discord.ActivityType.streaming:
                embed.title = "📺 **Streaming (Unknown Type)**"
                embed.add_field(
                    name="",
                    value=f"> **Title**:\n> {activity.name}\n\n**Platform**:\n> {activity.platform}",
                    inline=False
                )
                if activity.start:
                    embed.add_field(name="Started at:", inline=False,
                                    value=f"{discord.utils.format_dt(activity.start, style='R')} ({discord.utils.format_dt(activity.start)})")
            else:
                embed.title = "**Unknown Activity**"
                embed.add_field(
                    name="",
                    value=f"> **Activity**:\n> {activity.name}",
                    inline=False
                )
                if activity.start:
                    embed.add_field(name="Started at:", inline=False,
                                    value=f"{discord.utils.format_dt(activity.start, style='R')} ({discord.utils.format_dt(activity.start)})")
        await ctx.send(activities)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Miscellaneous(bot))
