import discord
import datetime
import asyncio
import aiohttp
import random
import config
import pendulum
from discord import Spotify
from discord.ext import commands
from discord.ext.commands import BucketType
from discord.ext.commands.errors import MissingRequiredArgument, CommandOnCooldown

class Miscellaneous(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.base_url = 'https://api.jikan.moe/v3/'
        self.session = aiohttp.ClientSession()

    @commands.command()
    @commands.guild_only()
    async def apply(self, ctx, member: discord.Member = None):
        """> Start a new application"""

        q_list = [
            "What\'s your IGN (In-Game-Name)?",
            "What\'s your UID?",
            "What\'s your age?",
            "Where are you from (Which country)",
            "What device are you playing on?",
            "Have you played for other clan before? If yes, please give a list.",
            "Are you still playing for a clan?",
            "Briefly tell us why would you like to join",
            "How much time do you spend on playing CODM?",
            "Are you available for VC (Voice Chat)",
            "Send your stats (in-link)"
        ]

        member = ctx.author if not member else member

        def checkmsg(m):
            return m.author == member

        def checkreact(reaction, user):
            return user.id == member.id and str(reaction.emoji) in ['✅', '❌']

        try:
            embed_start = discord.Embed(title=f"Application started in dm by {member}",
                                        description="The Questions will be sent shortly...",
                                        colour=discord.Colour.from_rgb(250, 0, 0))
            async with member.typing():
                await asyncio.sleep(1)
            await member.send("Send your stats")
            msg = await self.bot.wait_for('message', check=checkmsg, timeout=250.0)
            if msg.attachments:
                attachment_urls = []
                for attachment in msg.attachments:
                    attachment_urls.append(f'[{attachment.filename}]({attachment.url}) '
                                           f'({attachment.size} bytes)')
                msg = '\N{BULLET} ' + '\n\N{BULLET} '.join(attachment_urls)
            try:
                zeroth = msg.content
            except:
                zeroth = msg
            await ctx.send(embed=embed_start)
            async with member.typing():
                await asyncio.sleep(3)
            await member.send("What's your IGN (In-Game-Name)?")
            msg = await self.bot.wait_for('message', check=checkmsg, timeout=250.0)
            first = msg.content
            async with member.typing():
                await asyncio.sleep(1)
            await member.send(
                "What's your UID?")
            msg = await self.bot.wait_for('message', check=checkmsg, timeout=250.0)
            second = msg.content
            async with member.typing():
                await asyncio.sleep(1)
            await member.send(
                "What's your age?")
            msg = await self.bot.wait_for('message', check=checkmsg, timeout=250.0)
            third = msg.content
            async with member.typing():
                await asyncio.sleep(1)
            await member.send("Where are you from (Which country)")
            msg = await self.bot.wait_for('message', check=checkmsg, timeout=250.0)
            fourth = msg.content
            async with member.typing():
                await asyncio.sleep(1)
            await member.send("What device are you playing on?")
            msg = await self.bot.wait_for('message', check=checkmsg, timeout=250.0)
            fifth = msg.content
            async with member.typing():
                await asyncio.sleep(1)
            await member.send("Have you played for other clan before? If yes, please give a list.")
            msg = await self.bot.wait_for('message', check=checkmsg, timeout=250.0)
            sixth = msg.content
            async with member.typing():
                await asyncio.sleep(1)
            await member.send("Are you still playing for a clan?")
            msg = await self.bot.wait_for('message', check=checkmsg, timeout=250.0)
            seventh = msg.content
            async with member.typing():
                await asyncio.sleep(1)
            await member.send("Briefly tell us why would you like to join")
            msg = await self.bot.wait_for('message', check=checkmsg, timeout=250.0)
            eighth = msg.content
            async with member.typing():
                await asyncio.sleep(1)
            await member.send("How much time do you spend on playing CODM?")
            msg = await self.bot.wait_for('message', check=checkmsg, timeout=250.0)
            nineth = msg.content
            async with member.typing():
                await asyncio.sleep(1)
            await member.send("Are you available for VC (Voice Chat)")
            msg = await self.bot.wait_for('message', check=checkmsg, timeout=250.0)
            tenth = msg.content


        except asyncio.TimeoutError:
            await member.send("You took too long to write in a response :(")
        else:
            channel = self.bot.get_channel(config.LOG_ID)
            submit = await member.send("Are you sure you want to submit this application?")
            await submit.add_reaction('✅')
            await submit.add_reaction('❌')
            reaction, user = await self.bot.wait_for("reaction_add", timeout=600.0, check=checkreact)
            if str(reaction.emoji) == '✅':
                async with member.typing():
                    await asyncio.sleep(2)
                await member.send('Thank you for applying! Your application will be sent to the Owner soon')
                await asyncio.sleep(2)
                embed = discord.Embed(colour=discord.Colour.from_rgb(250, 0, 0))

                fields = [(q_list[0], first, False), (q_list[1], second, False), (q_list[2], third, False),
                          (q_list[3], fourth, False), (q_list[4], fifth, False), (q_list[5], sixth, False),
                          (q_list[6], seventh, False), (q_list[7], eighth, False), (q_list[8], nineth, False),
                          (q_list[9], tenth, False), (q_list[10], zeroth, False)]

                embed.add_field(name="User", value=f"{msg.author.mention} | {msg.author.id}", inline=False)

                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)

                embed.set_author(name=f"Application taken by: {member}", icon_url=f"{member.avatar_url}")
                embed.set_footer(text=f"{ctx.guild.name}")
                embed.timestamp = datetime.datetime.utcnow()
                embed_finished = await channel.send(embed=embed)
                await embed_finished.add_reaction('✅')
                await embed_finished.add_reaction('❌')
            else:
                if str(reaction.emoji) == '❌':
                    await member.send('Application won\'t be sent')

    @commands.cooldown(3, 5, commands.BucketType.user)
    @commands.group(invoke_without_command=True, aliases=['mal', 'ani'])
    async def anime(self, ctx, *, query):
        """> Searching for an anime and getting the response"""
        query = query.replace(' ', '/')
        api = self.base_url + f'search/anime?q={query}&page=1'
        async with self.session.get(url=api) as response:
            if response.status == 200:
                request = await response.json()
            elif response.status == 404:
                return await ctx.send("Invalid name.")
            else:
                return await ctx.send('The API is having some issues right now. Try again later.')
        await self.pagination(ctx, request)

    @commands.cooldown(3, 5, commands.BucketType.user)
    @anime.command(aliases=['char'])
    async def character(self, ctx, *, query):
        """> Searching for a character and getting the response"""
        query = query.replace(' ', '/')
        api = self.base_url + f'search/character?q={query}&page=1'
        async with self.session.get(url=api) as response:
            if response.status == 200:
                request = await response.json()
            elif response.status == 404:
                return await ctx.send("Invalid name.")
            else:
                return await ctx.send('The API is having some issues right now. Try again later.')

        await self.pagination(ctx, request, "char")

    async def pagination(self, ctx, content, type='anime'):
        """> Paginating the content from the requests"""
        embeds = []
        reactions = ['⏮', '◀', '🛑', '▶', '⏭']
        if type == "anime":
            for result in content['results'][:10]:
                e = discord.Embed(title=f'{result["title"]}', colour=discord.Colour.from_rgb(250, 0, 0))

                e.add_field(name='Description', value=f'{result["synopsis"]}')
                e.set_thumbnail(url=result["image_url"])
                status = 'Airing' if result['airing'] else 'Finished'
                e.add_field(name='⏳ Status', value=status)
                e.add_field(name='🗂️ Type', value=result["type"], inline=True)

                time = result["start_date"].split('-')

                if int(time[0]) > datetime.datetime.today().year:
                    st = f"19{time[0][-2:]}-{time[1]}-{time[2]}"
                else:
                    st = result["start_date"]
                start_date = st.split('T')[0]
                start = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()

                if not result["airing"]:
                    e_time = result["end_date"].split('-')

                    if int(e_time[0]) > datetime.datetime.today().year:
                        et = f"19{e_time[0][-2:]}-{e_time[1]}-{e_time[2]}"
                    else:
                        et = result["end_date"]
                    end_date = et.split('T')[0]
                    end = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
                else:
                    end = "?"

                if result["score"] == 0:
                    score = "N/A"
                else:
                    score = result["score"]

                e.add_field(name='🗓️ Aired', value=f'From **{start}** to **{end}**', inline=False)
                e.add_field(name='💽 Episodes', value=result["episodes"] or '?')
                e.add_field(name='⭐ Score', value=score, inline=True)
                e.add_field(name='\u200b', value=f'[Link]({result["url"]})', inline=False)
                embeds.append(e)

        elif type == "char":
            for result in content["results"][:20]:
                e = discord.Embed(title=f'{result["name"].replace(",", "")}', colour=discord.Colour.from_rgb(250, 0, 0))
                e.set_image(url=result["image_url"])
                x = result["alternative_names"]
                if x:
                    alt = '\n'.join(x)
                else:
                    alt = 'None'

                if result["anime"]:
                    ani_res = f'[{result["anime"][0]["name"]}]({result["anime"][0]["url"]})'
                    if len(result["anime"]) > 1:
                        ani_res += f'\n[{result["anime"][1]["name"]}]({result["anime"][1]["url"]})'
                    e.add_field(name='Anime', value=ani_res, inline=False)

                if result["manga"]:
                    manga_res = f'[{result["manga"][0]["name"]}]({result["manga"][0]["url"]})'
                    if len(result["manga"]) > 1:
                        manga_res += f'\n[{result["manga"][1]["name"]}]({result["manga"][1]["url"]})'

                    e.add_field(name='Manga', value=manga_res, inline=False)
                e.add_field(name='Alternative Names', value=alt, inline=False)
                e.add_field(name='\u200b', value=f'[{result["name"].replace(",", "")}]({result["url"]})')
                embeds.append(e)

        embeds[0].set_footer(text=f"Page: 1/{len(embeds)}")
        msg = await ctx.send(embed=embeds[0])
        for reaction in reactions:
            await msg.add_reaction(reaction)

        total_pages = len(embeds) - 1
        current_page = 0

        def check(reaction, user):
            """Checking messages reactions"""
            message_check = False
            user_check = False
            channel_check = False
            react_check = False

            if reaction.message.id == msg.id:
                message_check = True
            if user.id == ctx.author.id:
                user_check = True
            if reaction.message.channel.id == msg.channel.id:
                channel_check = True
            if str(reaction.emoji) in reactions:
                react_check = True

            return all([message_check, user_check, channel_check, react_check])

        while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=300.0)
            except asyncio.TimeoutError:
                await msg.clear_reactions()
                return
            else:

                if str(reaction.emoji) == reactions[0]:  # first page
                    current_page = 0

                elif str(reaction.emoji) == reactions[1]:  # one page back
                    current_page -= 1
                    if current_page < 0:
                        current_page = total_pages

                elif str(reaction.emoji) == reactions[2]:  # stop
                    await msg.clear_reactions()
                    return

                elif str(reaction.emoji) == reactions[3]:  # one page forward
                    current_page += 1
                    if current_page > total_pages:
                        current_page = 0

                elif str(reaction.emoji) == reactions[4]:  # last page
                    current_page = total_pages

                await msg.remove_reaction(str(reaction.emoji), ctx.author)
                embeds[current_page].set_footer(text=f'Page: {current_page + 1}/{total_pages + 1}')
                await msg.edit(embed=embeds[current_page])

    @anime.error
    async def error_handler(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            await ctx.send("No name provided")
        elif isinstance(error, CommandOnCooldown):
            await ctx.send("**Wait! You are on cooldown!**")
        else:
            raise error

    @character.error
    async def char_error(self, ctx, error):
        await self.error_handler(ctx, error)


    @commands.command(aliases=["toss", "flip"])
    @commands.guild_only()
    async def coinflip(self, ctx):
        """> Coin flip!"""
        await ctx.send(f"**{ctx.author.name}** flipped a coin and got **{random.choice(['Heads','Tails'])}**!")

    @commands.command()
    async def spotify(self, ctx, user: discord.Member = None):
        """> Get info of spotify song [user] is listening to"""
        user = user or ctx.author
        for activity in user.activities:
            if isinstance(activity, Spotify):
                embed = discord.Embed(color=activity.color)
                embed.title = f'{user.name} is listening to {activity.title}'
                embed.set_thumbnail(url=activity.album_cover_url)
                embed.description = f"Song Name: {activity.title}\nSong Artist: {activity.artist}\nSong Album: {activity.album}\
                    \nSong Lenght: {pendulum.duration(seconds=activity.duration.total_seconds()).in_words(locale='en')}"
            await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 50000, BucketType.user)
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
                color=discord.Color.from_rgb(250, 0, 0),
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

def setup(bot):
    bot.add_cog(Miscellaneous(bot))