import discord
from discord.ext import commands
import json
import os

class ConfigCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_file = 'config.json'
        self.config_data = self.load_config()

    def load_config(self):
        """Load the configuration data from config.json."""
        if not os.path.exists(self.config_file):
            # If the config file doesn't exist, create an empty one
            self.save_config({})
            return {}

        with open(self.config_file, 'r') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {}
                self.save_config(data)

        return data

    def save_config(self, data):
        """Save the configuration data to config.json."""
        with open(self.config_file, 'w') as file:
            json.dump(data, file, indent=4)

    @commands.has_permissions(administrator=True)
    @commands.command(name='set_channel')
    async def set_channel(self, ctx, channel_type: str, channel: discord.TextChannel):
        """Set a channel as important (welcome, rules, etc.)."""
        if channel_type not in ["welcome", "rules", "memes", "logs", "support"]:
            await ctx.send("Invalid channel type! Use 'welcome' or 'rules'.")
            return
        
        # Update the config with the new channel ID
        guild_id = str(ctx.guild.id)
        if guild_id not in self.config_data:
            self.config_data[guild_id] = {}
        
        important_channels = self.config_data[guild_id].get('important_channels', {})
        important_channels[channel_type] = str(channel.id)
        self.config_data[guild_id]['important_channels'] = important_channels

        # Save the updated config
        self.save_config(self.config_data)

        await ctx.send(f"Set {channel_type} channel to {channel.name}.")

    @commands.has_permissions(administrator=True)
    @commands.command(name='set_category')
    async def set_category(self, ctx, category_name: str, category: discord.CategoryChannel):
        """Set a category as important."""
        if category_name != "important":
            await ctx.send("Invalid category! Use 'important'.")
            return
        
        # Update the config with the new category ID
        guild_id = str(ctx.guild.id)
        if guild_id not in self.config_data:
            self.config_data[guild_id] = {}

        self.config_data[guild_id]['important_categories'] = {
            "important": str(category.id)
        }

        # Save the updated config
        self.save_config(self.config_data)

        await ctx.send(f"Set important category to {category.name}.")

    @commands.has_permissions(administrator=True)
    @commands.command(name='get_config')
    async def get_config(self, ctx):
        """Display the current important channels and categories."""
        guild_id = str(ctx.guild.id)
        if guild_id not in self.config_data:
            await ctx.send("No configuration found for this guild.")
            return
        
        important_channels = self.config_data[guild_id].get('important_channels', {})
        important_categories = self.config_data[guild_id].get('important_categories', {})

        response = "**Current Configuration:**\n"
        
        for channel_type, channel_id in important_channels.items():
            channel = self.bot.get_channel(int(channel_id))
            response += f"{channel_type.capitalize()} channel: {channel.name if channel else 'Not found'}\n"
        
        for category_name, category_id in important_categories.items():
            category = self.bot.get_channel(int(category_id))
            response += f"{category_name.capitalize()} category: {category.name if category else 'Not found'}\n"

        await ctx.send(response)

    @commands.has_permissions(administrator=True)
    @commands.command(name='remove_channel')
    async def remove_channel(self, ctx, channel_type: str):
        """Remove a channel from the important configuration."""
        if channel_type not in ["welcome", "rules"]:
            await ctx.send("Invalid channel type! Use 'welcome' or 'rules'.")
            return
        
        guild_id = str(ctx.guild.id)
        if guild_id not in self.config_data or 'important_channels' not in self.config_data[guild_id]:
            await ctx.send("No important channels configured.")
            return

        important_channels = self.config_data[guild_id]['important_channels']
        if channel_type not in important_channels:
            await ctx.send(f"{channel_type.capitalize()} channel is not set.")
            return
        
        # Remove the channel from the config
        del important_channels[channel_type]
        self.config_data[guild_id]['important_channels'] = important_channels
        self.save_config(self.config_data)

        await ctx.send(f"Removed {channel_type} channel from the important channels.")

    @commands.has_permissions(administrator=True)
    @commands.command(name='remove_category')
    async def remove_category(self, ctx):
        """Remove the important category."""
        guild_id = str(ctx.guild.id)
        if guild_id not in self.config_data or 'important_categories' not in self.config_data[guild_id]:
            await ctx.send("No important category configured.")
            return

        important_categories = self.config_data[guild_id]['important_categories']
        if 'important' not in important_categories:
            await ctx.send("Important category is not set.")
            return
        
        # Remove the category from the config
        del important_categories['important']
        self.config_data[guild_id]['important_categories'] = important_categories
        self.save_config(self.config_data)

        await ctx.send("Removed important category from the configuration.")

# Setup the cog
async def setup(bot):
    await bot.add_cog(ConfigCog(bot))
