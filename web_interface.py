from quart import Quart, render_template, request
import json
from database import Database
from discord_client import client as bot
import pprint

app = Quart('WumboDB')


@app.route('/')
async def main():
    db: Database = bot.get_cog("DatabaseCmds").db
    name = db.guild.name if db.guild else "none"

    temp_lines = "Data will show up here after you query the database."

    return await render_template("index.html", user=str(bot.user),
                                 server=name, loglines=temp_lines)


@app.route('/database_action', methods=['POST'])
async def database_action():
    form = await request.form

    db: Database = bot.get_cog("DatabaseCmds").db

    try:

        if form["operation"] == "create":
            data = json.loads(form["content"])
            id = await db.create_document(form["collection"], data)

            lines = f"Document created with id {id}."

        elif form["operation"] == "read":
            if form["identifier"].isnumeric():
                id, data = await db.read_document(form["collection"],
                                                int(form["identifier"]))
            else:
                id, data = await db.read_document(form["collection"],
                                                json.loads(form["identifier"]))
            lines = pprint.PrettyPrinter(indent=4).pformat(data) + \
                f"\n\nid: {id}"

        elif form["operation"] == "update":
            data = json.loads(form["content"])

            if form["identifier"].isnumeric():
                id = await db.update_document(form["collection"],
                                         int(form["identifier"]), data)
            else:
                id = await db.update_document(form["collection"],
                                         json.loads(form["identifier"]), data)

            lines = f"Update successful on document with id {id}."

        elif form["operation"] == "delete":
            if form["identifier"].isnumeric():
                id, data = await db.delete_document(form["collection"],
                                                    int(form["identifier"]))
            else:
                id, data = await db.delete_document(form["collection"],
                                                    json.loads(form["identifier"]))
            lines = "Successful deletion."

    except Exception as e:
        lines = "ERROR: " + str(e)

    return await render_template("index.html", user=str(bot.user),
                                 server=db.guild.name, loglines=lines)
