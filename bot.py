import json
from discord.ext import commands

config = json.load(open('config.json'))

client = commands.Bot(command_prefix=config['prefix'])


@client.command()
@commands.has_permissions(administrator=True)
async def reload(ctx):
    client.unload_extension('cogs.command_status')
    client.load_extension('cogs.command_status')
    await ctx.send("Reloaded.")
    print("Reloaded command_status cog.")

client.load_extension('cogs.command_status')
client.run(config['token'])
# Tab contributed by adding this line
