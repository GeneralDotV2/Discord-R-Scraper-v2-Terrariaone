import json
import requests
import datetime
import asyncio
import discord
from discord.ext import commands


class Info:
    def __init__(self):
        self.url = "https://api.terraria.one/"
        self.name = []
        self.servers = []
        self.count = 0

    def add_server(self, name, server_id):
        self.name.append(name)
        self.servers.append(server_id)
        self.count += 1

    def get_name(self, index):
        return self.name[index]

    def get_count(self):
        return self.count

    def get_info(self):
        servers_all_info = []
        for serv in self.servers:
            servers_all_info.append(json.loads(requests.request("GET", self.url + serv,  timeout=5).text))
        servers_info = []

        for infos in servers_all_info:
            servers_info.append([
                    infos["serverversion"],
                    infos["playercount"],
                    infos["maxplayers"],
                    infos["uptime"],
                    infos["players"],
					infos["name"],
                ])

        return servers_info


servers = json.load(open("servers.json"))
info = Info()
for server in servers:
    info.add_server(servers[server]["name"], servers[server]["server"])


class Status(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def status(self, ctx):
        p_info = info.get_info()
        await self.client.change_presence(
            status=discord.Status.dnd,
            activity=discord.Activity(
                name=f"{info.get_count()} lobbies", type=discord.ActivityType.watching
            ),
        )
        count_sum = 0
        for x in range(info.get_count()):
            count_sum += p_info[x][0]
        embed = discord.Embed(
            color=0xCE422B,
            title=f"Factorio NAEAST - Playing Online: ({count_sum}/{100 * info.get_count()})",
        )
        for x in range(info.get_count()):
            nicknames = "> ```"
            if p_info[x][4]:
                for nickname in p_info[x][4]:
                    nicknames += f"{nickname}, "
                nicknames = nicknames[:-2]
            else:
                nicknames += "No players online"
            nicknames += "```"
            embed.add_field(
                name=f"{info.get_name(x)}: ({p_info[x][0]}/{100})",
                value=nicknames,
                inline=False,
            )
            embed.add_field(name="Version: ", value=f"{p_info[x][2]}")
            embed.add_field(name="Map Time: ", value=f"{p_info[x][1]}")
        message = await ctx.send(embed=embed)
        message_id = message.id
        channel_id = message.channel.id
        guild_id = message.guild.id

        with open("config.json") as f:
            config = json.load(f)
        config["message_id"] = message_id
        config["channel_id"] = channel_id
        config["guild_id"] = guild_id

        with open("config.json", "w") as f:
            json.dump(config, f, indent=2)

    @commands.Cog.listener()
    async def on_ready(self):
        while True:
            try:
                p_info = info.get_info()
                now = datetime.datetime.now()
                current_time = str(now.strftime("%I:%M:%S"))
                await self.client.change_presence(
                    status=discord.Status.dnd,
                    activity=discord.Activity(
                        name=f"{info.get_count()} servers",
                        type=discord.ActivityType.watching,
                    ),
                )
                count_sum = 0
                for x in range(info.get_count()):
                    count_sum += p_info[x][1]
                embed = discord.Embed(
                    color=0x800080,
                    title=f"Terraria.one - Playing Online: ({count_sum}/{100 * info.get_count()})",
                )
                for x in range(info.get_count()):
                    usernames = " > ```"
                    if p_info[x][1]:
                        players = p_info[x][4]
                        for nick in p_info[x][4]:
                            print (nick)
                        


                    if nick == '':
                        nick += "{'nickname': 'test', 'username': ''}"
                        print(nick)
                    embed.add_field(name=f"{p_info[x][5]} - Players Online", value= "> ```" + "{}".format(', '.join(str(nick['nickname']) for nick in p_info[x][4])) + " ```", inline=False)
                    embed.add_field(name="Realm Uptime: ", value=f"{p_info[x][3]}", inline=True)
                    embed.add_field(name="Server Version: ", value=f"{p_info[x][0]}", inline=True)
                embed.set_footer(text="Last updated: " + current_time + " CST")
                embed.set_thumbnail(url="https://terraria.one/staticdata/tm/t1_logo_v2_1.png")
                ids = json.load(open("config.json"))
                msg = (
                    await self.client.get_guild(ids["guild_id"])
                    .get_channel(ids["channel_id"])
                    .fetch_message(ids["message_id"])
                )
                await msg.edit(embed=embed)
            except:
                pass
            await asyncio.sleep(15)


def setup(client):
    client.add_cog(Status(client))
