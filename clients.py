from discord.ext import commands
import discord
import os
import asyncio
from aiohttp.client import ClientSession
from dotenv.main import load_dotenv


class AsyncHttpRequest:
    """ All HTTP methods """
    def __init__(self):
        load_dotenv()
        self.session = None
        token = os.getenv("TOKEN")
        self.headers = {"Authorization": f'Bot {token}'}
        self.base_url = "https://discord.com/api"

    async def create_dm_channel(self, user_id):
        """ Creating an active dm channel between the bot and the invited user """
        if self.session is None:
            self.session = ClientSession()
        async with self.session.post(url=f"{self.base_url}/users/@me/channels",
                                     json={"recipient_id": user_id}, headers=self.headers) as response:
            return await response.json()

    async def init_multiple_dm_channels(self, users_id):
        """ requesting multiple create channel requests """
        results = await asyncio.gather(*[self.create_dm_channel(user) for user in users_id], return_exceptions=True)
        return results

    async def get_guild_members(self, guild_id):
        """ Getting all the server members that the users chose """
        if self.session is None:
            self.session = ClientSession()
        async with self.session.get(url=f"{self.base_url}/guilds/{guild_id}/members", headers=self.headers,
                                    params={"limit": 1000}) as response:
            return await response.json()

    async def send_inv_dm(self, chat_ids, invite):
        """ The invite msg the invited user is receiving """
        if self.session is None:
            self.session = ClientSession()
        async with self.session.post(url=f"{self.base_url}/channels/{chat_ids}/messages",
                                     json={"content": f"Your Friend is inviting you to study {invite}"},
                                     headers=self.headers) as response:
            return await response.json()

    async def inv_multiple_users(self, chat_ids, invite):
        results = await asyncio.gather(*[self.send_inv_dm(id, invite) for id in chat_ids], return_exceptions=True)
        return results

    async def create_voice_channel(self, guild_id, channel_name, users_limit):
        """ Creates a voice channel for the invited users to study in """
        if self.session is None:
            self.session = ClientSession()
        # Channel settings
        channel = {
            "name": channel_name if channel_name else "No Topic Study Room",
            "type": 2,
            "user_limit": users_limit,
        }
        async with self.session.post(url=f"{self.base_url}/guilds/{guild_id}/channels", headers=self.headers,
                                     json=channel) as response:
            return await response.json()

    async def create_invite(self, channel_id):
        """ Creating the invite link for the study session """
        if self.session is None:
            self.session = ClientSession()
        invite = {
            "max_age": 900,
            "max_uses": 2,
        }
        async with self.session.post(url=f"{self.base_url}/channels/{channel_id}/invites", headers=self.headers,
                                     json=invite) as response:
            response = await response.json()
            inv_code = response["code"]
            invite_msg = f"https://discord.gg/{inv_code}"
            return invite_msg

    async def delete_channel(self, channel_id):
        if self.session is None:
            self.session = ClientSession()
        async with self.session.delete(url=f"{self.base_url}/channels/{channel_id}", headers=self.headers) as response:
            response = await response.json()
        return response


class DiscordClient(commands.Cog):
    """ Discord bot client """
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        self.bot = commands.Bot(command_prefix="!", intents=intents)
        for filename in os.listdir("cogs"):
            if filename.endswith(".py") and filename != "__init__.py":
                self.bot.load_extension(f'cogs.{filename[:-3]}')