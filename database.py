import json
import io
import discord
from discord.ext import commands
from typing import Union
import imghdr


class DocIdent:
    # Structure used to identify documents
    # Can either identify using message id or using content
    def __init__(self, query):
        if type(query) == int:
            self.id: int = query
            self.query = None
        elif type(query) == dict:
            self.id = None
            self.query: dict = query

    @property
    def finder(self):
        # Used in discord.utils.find
        def check(message: discord.Message):
            if self.id:
                # Always prefer ID
                return message.id == self.id
            elif self.query:
                if not message.content:
                    return False

                data: dict = json.loads(message.content[3:-3])
                return data.items() >= self.query.items()
                # Return true only if it's a subset
            else:
                raise Exception
        return check


class Database():
    '''
    Core module of the discord database
    '''
    def __init__(self, bot: commands.Bot):
        self.bot: "commands.Bot" = bot

        self.guild: "discord.Guild" = None
        self.control_channel: "discord.TextChannel" = None
        self.collections: "dict[str, discord.TextChannel]" = {}
        print(f"WumboDB Starting... Waiting for connection to Discord.")

    async def startup(self, relay_id: int):
        '''
        Runs during startup to set up the databases
        Wait until bot is ready, and then load relay stuff
        '''
        self.guild = self.bot.get_guild(relay_id)

        if self.guild:
            print(f"Wumbo Relay connected to server: {self.guild.name}")
        else:
            print(f"Wumbo Relay not connected! Attempted connection id: {relay_id}")

        if not (channel := discord.utils.get(
                self.guild.text_channels, name="control")):
            self.control_channel = await self.guild.create_text_channel(
                                   "control")
            print("Setting up server for WumboDB (first time init)")
        else:
            self.control_channel = channel

        self.collections = {channel.name: channel for channel
                            in self.guild.text_channels if
                            channel != self.control_channel}
        # Set up collection mapping

    async def create_collection(self, name: str) -> None:
        '''
        Create a collection
        '''
        ch = await self.guild.create_text_channel(name)
        self.collections[ch.name] = ch

    async def delete_collection(self, name: str) -> None:
        '''
        Delete a collection
        '''
        channel = discord.utils.get(self.guild.text_channels, name=name)
        await channel.delete()
        del self.collections[name]

    async def rename_collection(self, name: str, new_name: str) -> None:
        '''
        Rename a collection
        '''
        channel = discord.utils.get(self.guild.text_channels, name=name)
        await channel.edit(name=new_name)
        del self.collections[name]

        ch = await self.bot.fetch_channel(channel.id)  # force refresh
        self.collections[ch.name] = ch

    async def create_document(self, collection: str, data: dict) -> int:
        '''
        Create a document in a collection.
        Returns: id of message
        '''
        if collection not in self.collections:
            raise ValueError(f"Collection {collection} does not exist.")

        msg = await self.collections[collection].\
            send(f"```{json.dumps(data)}```")
        return msg.id

    async def read_document(self, collection: str,
                            identifier: Union[int, dict]) -> "tuple(int,dict)":
        '''
        Retrieves document, by message ID or filter.
        Returns: Message ID, data.
        '''
        if collection not in self.collections:
            raise ValueError(f"Collection {collection} does not exist.")

        msg: discord.Message = \
            await self.collections[collection].history(limit=None).\
            find(DocIdent(identifier).finder)
        if not msg:
            raise ValueError("No suitable documents found!")
        data: dict = json.loads(msg.content[3:-3])
        return msg.id, data

    async def delete_document(self, collection: str,
                              identifier: Union[int, dict]):
        '''
        Deletes document in a collection, by message ID or filter.
        '''
        if collection not in self.collections:
            raise ValueError(f"Collection {collection} does not exist.")

        msg: discord.Message = \
            await self.collections[collection].history(limit=None).\
            find(DocIdent(identifier).finder)
        await msg.delete()

    async def update_document(self, collection: str,
                              identifier: Union[int, dict], data: dict) -> int:
        '''
        Updates document in a collection, by message ID or filter.
        '''
        if collection not in self.collections:
            raise ValueError(f"Collection {collection} does not exist.")

        msg: discord.Message = \
            await self.collections[collection].history(limit=None).\
            find(DocIdent(identifier).finder)
        await msg.edit(content=f"```{json.dumps(data)}```")
        return msg.id

    async def create_blob(self, collection: str,
                          data: io.BufferedIOBase) -> int:
        '''
        Create a blob (file) in a collection.
        Returns: id of blob
        '''
        if collection not in self.collections:
            raise ValueError(f"Collection {collection} does not exist.")

        if ext := imghdr.what(data):
            msg = await self.collections[collection].\
                send(file=discord.File(data, "attachment." + ext))
        else:
            msg = await self.collections[collection].\
                send(file=discord.File(data, "attachment"))

        return msg.id

    async def read_blob(self, collection: str, id: int) -> str:
        '''
        Retrieves document, by message ID.
        Returns: URI to blob
        '''
        if collection not in self.collections:
            raise ValueError(f"Collection {collection} does not exist.")

        msg: discord.Message = \
            await self.collections[collection].history(limit=None).get(id=id)
        return msg.attachments[0].url

    async def delete_blob(self, collection: str, id: int):
        '''
        Deletes blob in a collection, by message ID.
        '''
        if collection not in self.collections:
            raise ValueError(f"Collection {collection} does not exist.")

        msg: discord.Message = \
            await self.collections[collection].history(limit=None).get(id=id)
        await msg.delete()
