
import json
import os
import traceback
from typing import Literal

import discord
from discord import app_commands
from discord.ext import tasks
from keepalive import keep_alive
from string import capwords
from datetime import datetime
import database


class MenuClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        # The command tree holds the application slash command state.
        # The bot maintains its own tree similar to this when using @Bot.Command(
        self.tree = app_commands.CommandTree(self)


# Set discord intents
intents = discord.Intents.default()
bot = MenuClient(intents=intents)

# Display bot start up in console
@bot.event
async def on_ready():
    print("Running as {0.user}".format(bot))
    # Sync commands with every server the bot is in
    await bot.tree.sync()
    return


@bot.event
async def on_guild_join(guild: discord.Guild):
    """Ensure newly added servers can access slash commands"""
    print(f"Joined \"{guild.name}\" (guild id: {guild.id})")
    await bot.tree.sync(guild=guild)


async def get_todays_menu_as_embed(hall_id: int, meal: str) -> discord.Embed:
    """Create a discord embed message from today's menu

    :param hall_id: Dinning hall to get the menu for
    :param meal: Which meal to get a menu for (Breakfast, Lunch, Dinner)
    :return: A completely ready to post discord embed
    """
    hall_name = dininghallmenu.hall_name_from_id(hall_id)
    try:
        menu_dict = await dininghallmenu.get_todays_menu(hall_id, meal)

        # Create an embed message from the menu
        embed = discord.Embed(title=f"{capwords(meal)} at {hall_name}", color=dininghallmenu.colour_assiosiated_with_meal(meal))
        # Add every menu item into a field for its respective station
        for key in menu_dict:
            items_string = "\n".join(menu_dict[key])
            embed.add_field(name=key, value=items_string)

    # Let the users know what happened when a menu couldn't be found
    except dininghallmenu.HallClosedError:
        embed = discord.Embed(title=f"{hall_name} is not serving {capwords(meal)} today", color=0xb90e31)
    except (dininghallmenu.MenuApiError, json.JSONDecodeError) as error:
        description = "The menu format might have changed" if error is dininghallmenu.MenuApiError else \
            "The menus might have been moved again"
        embed = discord.Embed(title=f"{capwords(meal)} at {hall_name}", color=0x002452,
                              description="I ran into a problem finding the menu :(")
        embed.add_field(name="Issue", value=description)
        # Display the error in the log
        traceback.print_exception(error)
    return embed


@bot.tree.command()
@app_commands.describe(
    channel="(Optional) Which channel to post the menus in"
)
async def setmenuchannel(interaction: discord.Interaction, channel: discord.TextChannel = None):
    """
    Set which channel daily menus should be posted to.

    Defaults to the current channel when not provided.
    """
    # Only admins should be able to set where daily menus go
    if interaction.user.guild_permissions.administrator:
        # Default to the channel the user used the command in
        if channel is None:
            channel = interaction.channel

        # Register the channel as where this guild receives daily messages
        database.set_menu_channel(interaction.guild_id, channel.id)
        await interaction.response.send_message(f"Ok, I'll post automatic menus in #{channel.name}")
    else:
        await interaction.response.send_message("Sorry, you don't have permission to do that")


@bot.tree.command()
async def getmenuchannel(interaction: discord.Interaction):
    """Display which channel is set to receive daily menus"""
    channel_id = database.get_menu_channel(interaction.guild_id)
    if channel_id is None:
        await interaction.response.send_message("There isn't a channel selected for daily menus")
        return

    await interaction.response.send_message(f"Daily menus go in {bot.get_channel(channel_id).mention}")


@bot.tree.command()
async def forgetmenuchannel(interaction: discord.Interaction):
    """Stop sending daily menus to the guild"""
    # Only admins should be able to stop daily menu posts
    if interaction.user.guild_permissions.administrator:
        database.forget_menu_channel(interaction.guild_id)
        await interaction.response.send_message("Ok, I won't post daily menus in this server anymore")
    else:
        await interaction.response.send_message("Sorry, you don't have permission to do that")


@bot.tree.command()
@app_commands.describe(
    meal="Which meal to get the menu for",
    hall="The dinning hall to get the menu for"
)
async def menu(interation: discord.Interaction,
               meal: Literal["Breakfast", "Lunch", "Dinner"],
               hall: Literal["Leonard", "Ban Righ", "Jean Royce"]):
    """Get the menu for a specific meal at a dining hall"""
    if hall.lower() == "benry":
        await interation.response.send_message("Stop")
        return

    hall_id = dininghallmenu.hall_id_from_name(hall)
    if hall_id == -1:  # Invalid hall name entered
        print(f"Invalid hall name\"{hall}\" used")
        await interation.response.send_message("Sorry, I can only get the menu for Leonard, Ban Righ, and Jean Royce")
        return

    if not (meal.lower() == "breakfast" or meal.lower() == "lunch" or meal.lower() == "dinner"):
        await interation.response.send_message("I can only find menus for breakfast, lunch, and dinner")
        return

    # Get the menu from the queen's backend
    embed = await get_todays_menu_as_embed(hall_id, meal)

    await interation.response.send_message(embed=embed)

# -----------------------------------------------------------------------------------------------
# Make sure the table exists in the database
database.init_db()

# If this is running on REPL.IT, keep it alive after the tab closes with a web server
# Set up a pinging service to keep it alive longer than an hour
if "REPL_OWNER" in os.environ:
    keep_alive()
    print("Running on REPL.IT! Starting a keep-alive web-server.")
    print("To keep this bot running long after the tab closes, set up a pinging service.")
    

token = os.environ["TOKEN"]
bot.run(token)