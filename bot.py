import discord
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if TOKEN:
    print("✅ Token successfully loaded")
else:
    print("❌ Token failed to load, please check .env file")

API_URL_SEARCH = "https://api.quavergame.com/v2/user/search/"  # + username
API_URL_FULL = "https://api.quavergame.com/v2/user/"  # + id
USER_MAPPINGS_FILE = "user_mappings.json"

def load_user_mappings():
    if os.path.exists(USER_MAPPINGS_FILE):
        with open(USER_MAPPINGS_FILE, "r") as file:
            return json.load(file)
    return {}

def save_user_mappings(mappings):
    with open(USER_MAPPINGS_FILE, "w") as file:
        json.dump(mappings, file)

user_mappings = load_user_mappings()
last_searched_id = {}

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ Bot logged in as {client.user}')
    # Set the bot's activity to "Playing Quaver"
    activity = discord.Game(name="Quaver")
    await client.change_presence(status=discord.Status.online, activity=activity)

@client.event
async def on_message(message):
    print(f"Received message: {message.content}")

    if message.author == client.user:
        return

    if message.content.startswith("!link"):
        parts = message.content.split(" ")
        if len(parts) < 2:
            if str(message.author.id) in last_searched_id:
                quaver_id = last_searched_id[str(message.author.id)]
            else:
                embed = discord.Embed(
                    title="❌ Link failed",
                    description="Please use '!quaver' to look up a user first, or directly specify a username, for example: '!link Cookiezi'",
                    color=discord.Color.red()
                )
                await message.channel.send(embed=embed)
                return
        else:
            username = parts[1]
            try:
                response = requests.get(API_URL_SEARCH + username)
                response.raise_for_status()
                data = response.json()
                if data.get("users"):
                    quaver_id = data["users"][0]["id"]
                else:
                    embed = discord.Embed(
                        title="❌ User not found",
                        description=f"Quaver player not found **{username}**",
                        color=discord.Color.red()
                    )
                    await message.channel.send(embed=embed)
                    return
            except requests.exceptions.RequestException as e:
                embed = discord.Embed(
                    title="❌ API error",
                    description="API request failed, please try again later",
                    color=discord.Color.red()
                )
                await message.channel.send(embed=embed)
                print(f"API Error: {e}")
                return

        user_mappings[str(message.author.id)] = quaver_id
        save_user_mappings(user_mappings)
        embed = discord.Embed(
            title="✅ Link success",
            description=f"**{message.author.name}** linked to **{quaver_id}**",
            color=discord.Color.green()
        )
        await message.channel.send(embed=embed)
        return

    if message.content.startswith("!unlink"):
        if str(message.author.id) in user_mappings:
            del user_mappings[str(message.author.id)]
            save_user_mappings(user_mappings)
            embed = discord.Embed(
                title="✅ Unlink success",
                description=f"**{message.author.name}**'s Quaver ID unlinked",
                color=discord.Color.green()
            )
            await message.channel.send(embed=embed)
        else:
            embed = discord.Embed(
                title="❌ Not linked",
                description="You have not linked any Quaver user",
                color=discord.Color.red()
            )
            await message.channel.send(embed=embed)
        return

    if message.content.startswith("!quaver"):
        print(f"Command: !quaver triggered")
        parts = message.content.split(" ")
        if len(parts) < 2:  # No username provided
            if str(message.author.id) in user_mappings:
                quaver_id = user_mappings[str(message.author.id)]
                # Fetch user data using the stored quaver_id
                try:
                    response = requests.get(API_URL_FULL + str(quaver_id))
                    response.raise_for_status()
                    data = response.json()
                    user = data.get("user", {})
                    avatar_url = user.get("avatar_url")
                    embed = discord.Embed(
                        title=f"✅ Quaver Info for {user.get('username', 'Unknown')}",
                        description=f"Your Quaver ID: **{quaver_id}**",
                        color=discord.Color.blue()
                    )
                    if avatar_url:
                        embed.set_thumbnail(url=avatar_url)
                    await message.channel.send(embed=embed)
                except requests.exceptions.RequestException as e:
                    embed = discord.Embed(
                        title="❌ API error",
                        description="API request failed, please try again later",
                        color=discord.Color.red()
                    )
                    await message.channel.send(embed=embed)
                    print(f"API Error: {e}")
            else:
                embed = discord.Embed(
                    title="❌ Missing parameter",
                    description="Please enter a Quaver username, for example: `!quaver Cookiezi`",
                    color=discord.Color.red()
                )
                await message.channel.send(embed=embed)
        else:  # Username provided
            username = parts[1]
            try:
                response = requests.get(API_URL_SEARCH + username)
                response.raise_for_status()
                data = response.json()
                if data.get("users"):
                    user = data["users"][0]
                    quaver_id = user["id"]
                    avatar_url = user.get("avatar_url")
                    last_searched_id[str(message.author.id)] = quaver_id
                    embed = discord.Embed(
                        title=f"✅ Quaver Info for {username}",
                        description=f"Quaver ID: **{quaver_id}**",
                        color=discord.Color.blue()
                    )
                    # If there is an avatar URL, set it as a thumbnail
                    if avatar_url:
                        embed.set_thumbnail(url=avatar_url)
                    embed.set_footer(text="Use !link to directly link this ID")
                    await message.channel.send(embed=embed)
                else:
                    embed = discord.Embed(
                        title="❌ User not found",
                        description=f"Could not find Quaver data for **{username}**",
                        color=discord.Color.red()
                    )
                    await message.channel.send(embed=embed)
            except requests.exceptions.RequestException as e:
                embed = discord.Embed(
                    title="❌ API error",
                    description="API request failed, please try again later",
                    color=discord.Color.red()
                )
                await message.channel.send(embed=embed)
                print(f"API Error: {e}")

client.run(TOKEN)