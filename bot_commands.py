import io
from discord.ext import commands
from database import Database
from typing import Union
import json
import pprint


class DatabaseCmds(commands.Cog):
    '''
    Commands interface
    '''
    def __init__(self, bot: commands.Bot, db: Database):
        self.bot: "commands.Bot" = bot
        self.db: Database = db

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
            await self.db.create_collection(name)
            await ctx.send("Success", delete_after=5)
        except Exception as e:
            await ctx.send(str(e))

    @collection.command(name="delete")
    async def deletecollection(self, ctx: commands.Context, name: str):
        '''
        Delete a collection
        '''
        try:
            await self.db.delete_collection(name)
            await ctx.send("Success", delete_after=5)
        except Exception as e:
            await ctx.send(str(e))

    @collection.command(name="rename")
    async def renamecollection(self, ctx: commands.Context, old_name: str, new_name):
        '''
        Rename a collection
        '''
        try:
            await self.db.rename_collection(old_name, new_name)
            await ctx.send("Success", delete_after=5)
        except Exception as e:
            await ctx.send(str(e))

    @commands.command()
    async def create(self, ctx: commands.Context, collection: str, *, data: str):
        '''
        Create a document in a collection. Input in JSON format.
        '''
        try:
            j = json.loads(data)

            id = await self.db.create_document(collection, j)
            await ctx.send(f"Document created with id `{id}`")
        except Exception as e:
            await ctx.send(str(e))

    @commands.command()
    async def delete(self, ctx: commands.Context, collection: str, *, identifier: Union[int, str]):
        '''
        Deletes document in a collection. Can identify either by message ID or filter.
        '''
        try:
            if type(identifier) == str:
                j = json.loads(identifier)
                await self.db.delete_document(collection, j)
            else:
                await self.db.delete_document(collection, identifier)
            await ctx.send("Success", delete_after=5)
        except Exception as e:
            await ctx.send(str(e))

    @commands.command()
    async def update(self, ctx: commands.Context, collection: str, identifier: Union[int, str], *, data: str):
        '''
        Updates document in a collection. Can identify either by message ID or filter.
        '''
        try:
            new_data = json.loads(data)

            if type(identifier) == str:
                j = json.loads(identifier)
                await self.db.update_document(collection, j, new_data)
            else:
                await self.db.update_document(collection, identifier, new_data)
            await ctx.send("Success", delete_after=5)
        except Exception as e:
            await ctx.send(str(e))

    @commands.command()
    async def read(self, ctx: commands.Context, collection: str, *, identifier: Union[int, str]):
        '''
        Reads document in a collection. Can identify either by message ID or filter.
        '''
        try:
            if type(identifier) == str:
                j = json.loads(identifier)
                id, doc = await self.db.read_document(collection, j)
            else:
                id, doc = await self.db.read_document(collection, identifier)
            await ctx.send(f"```{pprint.PrettyPrinter(indent=4).pformat(doc)}```"
                           + f"\n\nID: `{id}`")
        except Exception as e:
            await ctx.send(str(e))

    @commands.group()
    async def blob(self, ctx: commands.Context):
        '''
        Parent command for blobs.
        '''
        if ctx.invoked_subcommand is None:
            await ctx.send(f"Subcommands: `create`, `read`, `delete`")

    @blob.command(name="create")
    async def createblob(self, ctx: commands.Context, collection: str):
        '''
        Create a blob in a collection. Input by attaching file.
        '''
        try:
            fp = io.BytesIO()
            await ctx.message.attachments[0].save(fp, seek_begin=True)
            id = await self.db.create_blob(collection, fp)
            await ctx.send(f"Blob created with id `{id}`")
        except Exception as e:
            await ctx.send(str(e))

    @blob.command(name="read")
    async def readblob(self, ctx: commands.Context, collection: str, id: int):
        '''
        Reads blob in a collection. Can identify by message ID.
        '''
        try:
            url = await self.db.read_blob(collection, id)
            await ctx.send(url)
        except Exception as e:
            await ctx.send(str(e))

    @blob.command(name="delete")
    async def deleteblob(self, ctx: commands.Context, collection: str, id: int):
        '''
        Deletes blob in a collection. Can identify by message ID.
        '''
        try:
            await self.db.delete_blob(collection, id)
            await ctx.send("Success", delete_after=5)
        except Exception as e:
            await ctx.send(str(e))
