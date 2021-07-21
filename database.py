import os
import discord
from discord.ext import commands
from typing import Union


class DocIdent:
    # Structure used to identify documents
    # Can either identify using message id or using content
    def __init__(self, query):
        if type(query) == int:
            self.id: int = query
            self.data = None
        elif type(query) == str:
            self.id: int = None
            self.data: str = query

    @property
    def searchterms(self):
        # Used in discord.utils.get
        if self.id:
            # Always prefer ID
            return {"id": self.id}
        elif self.data:
            return {"content": self.data}
        else:
            raise Exception


class Database(commands.Cog):
    '''
    Core module of the discord database
    '''
    def __init__(self, bot: commands.Bot):
        self.bot: "commands.Bot" = bot

        self.db_guild: "discord.Guild" = None
        self.control_channel: "discord.TextChannel" = None
        self.collections: "dict[str, discord.TextChannel]" = {}

    async def startup(self, relay_id: int):
        '''
        Runs during startup to set up the databases
        Wait until bot is ready, and then load relay stuff
        '''
        self.db_guild = self.bot.get_guild(relay_id)

        if self.db_guild:
            print(f"Relay connected to server: {self.db_guild.name}")
        else:
            print(f"Relay not connected! Attempted connection id: {relay_id}")

        if not (channel := discord.utils.get(
                self.db_guild.text_channels, name="control")):
            self.control_channel = await self.db_guild.create_text_channel(
                                   "control")
            print("Setting up server for database (first time init)")
        else:
            self.control_channel = channel

        self.collections = {channel.name: channel for channel in self.db_guild.text_channels if channel != self.control_channel}
        # Set up collection mapping

    @commands.Cog.listener()
    async def on_ready(self):
        await self.startup(int(os.environ.get("GUILD")))

    @commands.group()
    async def collection(self, ctx: commands.Context):
        '''
        Parent command for collections.
        '''
        if ctx.invoked_subcommand is None:
            await ctx.send(f"Subcommands: `create`, `rename`, `delete`")

    @collection.command(name="create")
    async def createcollection(self, ctx: commands.Context, name: str):
        '''
        Create a collection
        '''
        try:
            ch = await self.db_guild.create_text_channel(name)
            self.collections[ch.name] = ch

        except Exception as e:
            await ctx.send(f"Error: {e}")

    @collection.command(name="delete")
    async def deletecollection(self, ctx: commands.Context, name: str):
        '''
        Create a collection
        '''
        try:
            channel = discord.utils.get(self.db_guild.text_channels, name=name)
            await channel.delete()

            del self.collections[name]

        except Exception as e:
            await ctx.send(f"Error: {e}")

    @commands.command()
    async def create(self, ctx: commands.Context, collection: str, *, data: str):
        '''
        Create a document in a collection
        '''
        if collection not in self.collections:
            return
        await self.collections[collection].send(data)

    @commands.command()
    async def delete(self, ctx: commands.Context, collection: str, *, identifier: Union[int, str]):
        '''
        Deletes document in a collection
        '''
        if collection not in self.collections:
            return
        msg = await self.collections[collection].history().get(**DocIdent(identifier).searchterms)
        if not msg:
            await ctx.send("Not found")
        else:
            await msg.delete()

    @commands.command()
    async def update(self, ctx: commands.Context, collection: str, identifier: Union[int, str], *, data: str):
        '''
        updates document in a collection
        '''
        if collection not in self.collections:
            return
        msg = await self.collections[collection].history().get(**DocIdent(identifier).searchterms)
        if not msg:
            await ctx.send("Not found")
        else:
            await msg.edit(data)
