# WumboDB
A CRUD database, on Discord???

"[It's set to W, for Wumbo!](https://www.youtube.com/watch?v=--hsVknT1c0)"

# Introduction
WumboDB is a laughable mimicry of MongoDB using Discord.

Data is stored inside text channels inside servers, and accessed using a bot client.

## Perks
* COMPLETELY FREE TO USE with no data cap
* Uses *beautiful* Discord interface
* Up to 499 data collections per server used
* Database runs on rock solid Discord backend, > 99.9% Uptime

## Disadvantages
* It's a database implemented in Discord.
* Slow as a snail.
* Stores everything as text, and parses.
* This is a meme project LMAO

# Using it yourself
1. Clone the repo
2. Open up the folder
3. `pip install -r requirements.txt`
4. Make a bot at https://discord.com/developers/applications
5. Make a new Discord server, invite the bot, give it admin privs, copy the guild ID
6. Make a file called `.env`, with the format:
```
TOKEN = yourbottoken
GUILD = idofyourguild
```
7. Run `main.py` and enjoy the show
