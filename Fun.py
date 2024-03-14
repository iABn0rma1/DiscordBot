import discord
import asyncio
import random
from PIL import Image
from io import BytesIO
import config
from discord.ext import commands
from discord.ext.commands import BadArgument
from lists import *

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        botID = self.bot.get_user(config.BOT_ID)
        ownerID = self.bot.get_user(config.OWNER_ID)

    intents = discord.Intents.default()
    intents.members = True
    

    @commands.command()
    async def beer(self, ctx, user: discord.Member = None, *, reason: commands.clean_content = ""):
        """> Share a beer with someone"""
        if not user or user.id == ctx.author.id:
            return await ctx.send(f"**{ctx.author.mention}**: fieeeeestaaa!🎉🍺")
        if user.bot == True:
            return await ctx.send(
                f"I would love to give a beer to {user.mention}. But i am unsure they will respond to you!")

        beer_offer = f"**{user.mention}**, You have a 🍺 offered from **{ctx.author.mention}**"
        beer_offer = beer_offer + f"\n\n**Reason:** {reason}" if reason else beer_offer
        msg = await ctx.send(beer_offer)

        def reaction_check(m):
            if m.message_id == msg.id and m.user_id == user.id and str(m.emoji) == "🍻":
                return True
            return False

        try:
            await msg.add_reaction("🍻")
            await self.bot.wait_for('raw_reaction_add', timeout=30.0, check=reaction_check)
            await msg.edit(content=f"**{user.mention}** and **{ctx.author.mention}** Are enjoying a lovely 🍻")
            await msg.clear_reactions()
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.send(f"well it seems **{user.name}** didnt want a beer with **{ctx.author.name}** ;-;")
        except discord.Forbidden:
            beer_offer = f"**{user.name}**, you have a 🍺 from **{ctx.author.name}**"
            beer_offer = beer_offer + f"\n\n**reason:** {reason}" if reason else beer_offer
            await msg.edit(content=beer_offer)

    @commands.command()
    async def retard(self, ctx, user: discord.Member = None):
        """> See how retard user is, 100% official score"""
        if user == None:
            user = ctx.author
        else:
            pass
        embed = discord.Embed(
            title='',
            color=ctx.author.colour
        )
        embed.add_field(name='**retard r8 machine**', value=f'{user.display_name} is {random.randint(1,100)}% retarded')
        await ctx.send(embed=embed)

    @commands.command(aliases=['jokes'])
    async def joke(self, ctx):
        """> Sends a random PJ"""
        embed = discord.Embed(
            title='',
            color=discord.Color.from_rgb(250,0,0)
        )
        embed.add_field(name='**Joke**', value=f'{random.choice(joke)}')
        await ctx.send(embed=embed)

    @commands.command(aliases=['murder'])
    async def kill(self, ctx, *, user: discord.Member = None):
        """> Sick of someone? Easy! Just kill them! (we do not endorse murder yet BUT we do in **CODM**)"""
        if user == None or user == 'me':
            user = ctx.author
        else:
            pass
        e = discord.Embed(title="", description="", colour=ctx.author.colour)
        e.add_field(name=f'**How did they die**', value=(f'{user.display_name} was killed by {random.choice(died)}'))
        await ctx.send(embed=e)

    @commands.command(aliases=['predict'])
    @commands.guild_only()
    async def guess(self, ctx):
        """> Number guessing game"""
        await ctx.send('Guess a number between 1 and 10.')
        def is_correct(m):
            return m.author == ctx.author and m.content.isdigit()
        answer = random.randint(1, 10)
        try:
            guess = await self.bot.wait_for('message', check=is_correct, timeout=5.0)
        except asyncio.TimeoutError:
            return await ctx.send('Sorry, you took too long it was {}.'.format(answer))
        if int(guess.content) == answer:
            await ctx.send('You are right!')
        else:
            await ctx.send('Oops. You are wrong. It is actually {}.'.format(answer))

    @commands.command(aliases=["rekt"])
    @commands.guild_only()
    async def roast(self, ctx, member: discord.Member = None):
            """>  Sick of someone? Easy! Just roast them!"""
            await ctx.trigger_typing()
            if member is None:
                member = ctx.author
            if member == botID:
                return await ctx.send("Don't you dare doing that!")
            if member == ownerID:
                return await ctx.send("I'm not going to do that.")
            await ctx.send("{random.choice(roasts)}")

    @commands.command(aliases=["select", "pick"])
    @commands.guild_only()
    async def choose(self, ctx, *choices: str):
        """> Choose between multiple choices"""
        try:
            choice = "`" + '`, `'.join(choices) + "`"
            embed = discord.Embed(colour=ctx.author.colour,
                                  description=f"**Choices:** {choice}\n**I'd choose:** `{random.choice(choices)}`")
            await ctx.send(embed=embed)
        except IndexError:
            await ctx.send(f"❌ Can't choose from empty choices")

    @commands.command(aliases=["gayrate"])
    @commands.guild_only()
    async def howgay(self, ctx, *, user: discord.User = None):
        """> See how gay someone is (100% real)"""
        if user == botID or user == botID:
            return await ctx.send("Bot's can't be gay. You are so dumb!")
        if user == ownerID or user == ownerID:
            return await ctx.send(embed=discord.Embed(title="gay r8 machine", colour=discord.Colour.from_rgb(250,0,0),
                                                      description=f"{ctx.author.name} is 100% gay"))
        if user is None:
            user = ctx.author.name
        num = random.randint(0, 100)
        deci = random.randint(0, 9)
        if num == 100:
            deci = 0
        rating = f"{num}.{deci}"
        embed = discord.Embed(title='gay r8 machine',
                              description = f"{user.name} is {rating}% gay :rainbow_flag:",
                              colour=ctx.author.colour)
        await ctx.send(embed = embed)

    @commands.command(aliases=['simpr8', 'howsimp'])
    @commands.guild_only()
    async def simp(self, ctx, user: discord.Member = None):
        """> See how simp someone is, 100% official score"""
        if user is None:
            user = ctx.author
        if user == ownerID:
            return await ctx.send(embed = discord.Embed(title='simp r8 machine',
                                description=f"{user.name} is 100% simp",
                                colour=discord.Colour.from_rgb(250, 0, 0)))
        if user == botID:
            return await ctx.send("I'm a bot not a simp.")
        num = random.randint(0, 100)
        deci = random.randint(0, 9)
        if num == 100:
            deci = 0
        rating = f"{num}.{deci}"
        embed = discord.Embed(title='simp r8 machine',
                                description=f"{user.name} is {rating}% simp",
                                colour=ctx.author.colour)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    async def fight(self, ctx, user1: discord.Member, user2: discord.Member = None):
        """> Fight someone! Wanna fight with yourself? Leave [user2] empty"""
        if user2 == None:
            user2 = ctx.author
        if user1 == botID or user2 == botID:
            return await ctx.send("I'm not fighting with anyone.")
        if user1 == ownerID or user2 == ownerID:
            return await ctx.send("AB01 fucked you up so hard that you died immediately.")
        win = random.choice([user1, user2])
        if win == user1:
            lose = user2
        else:
            lose = user1
        responses = [
            f'That was intense battle, but unfortunatelly {win.mention} has beaten up {lose.mention} to death',
            f'That was a shitty battle, they both fight themselves to death',
            f'Is that a battle? You both suck',
            f'Yo {lose.mention} you lose! Ha',
            f'I\'m not sure how, but {win.mention} has won the battle']
        await ctx.send(f'{random.choice(responses)}')

    @commands.command()
    async def wanted(self, ctx, user: discord.Member = None):
        """> Excuse me ur under arrest"""
        if user is None:
            user = ctx.author

        wanted = Image.open("Wanted.jpg")

        asset = user.avatar_url_as(size=128)
        data = BytesIO(await asset.read())
        pfp = Image.open(data)

        pfp.resize((171, 153))

        wanted.paste(pfp, (91, 156))

        wanted.save("profile.png")

        await ctx.send(file=discord.File("profile.png"))

    @commands.command()
    async def disability(self, ctx, user: discord.Member = None):
        """> Not all disabilities look like you"""
        if user is None:
            user = ctx.author

        wanted = Image.open("disability.jpg")

        asset = user.avatar_url_as(size=128)
        data = BytesIO(await asset.read())
        pfp = Image.open(data)

        pfp.resize((151, 149))

        wanted.paste(pfp, (559, 416))

        wanted.save("profile.png")

        await ctx.send(file=discord.File("profile.png"))

def setup(bot):
    bot.add_cog(Fun(bot))