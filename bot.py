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
last_searched_id = {}  # 改為儲存最後查詢的 Quaver ID

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ Bot logged in as {client.user}')

@client.event
async def on_message(message):
    print(f"Received message: {message.content}")

    if message.author == client.user:
        return

    if message.content.startswith("!link"):
        parts = message.content.split(" ")
        if len(parts) < 2:  # 如果沒有指定參數
            if str(message.author.id) in last_searched_id:
                quaver_id = last_searched_id[str(message.author.id)]
            else:
                await message.channel.send("❌ **請先使用 !quaver 查詢一個用戶**，或直接指定 username，例如：`!link Cookiezi`")
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
                    await message.channel.send(f"❌ Couldn't find Quaver user **{username}**")
                    return
            except requests.exceptions.RequestException as e:
                await message.channel.send("❌ API request failed, please try again later")
                print(f"API Error: {e}")
                return

        user_mappings[str(message.author.id)] = quaver_id
        save_user_mappings(user_mappings)
        await message.channel.send(f"✅ **{message.author.name}** linked to Quaver ID **{quaver_id}**")
        return

    if message.content.startswith("!unlink"):
        if str(message.author.id) in user_mappings:
            del user_mappings[str(message.author.id)]
            save_user_mappings(user_mappings)
            await message.channel.send(f"✅ **{message.author.name}** Quaver user unlinked")
        else:
            await message.channel.send("❌ **You haven't linked a Quaver user yet**")
        return

    if message.content.startswith("!quaver"):
        print(f"Command: !quaver triggered")
        parts = message.content.split(" ")
        if len(parts) < 2:
            if str(message.author.id) in user_mappings:
                quaver_id = user_mappings[str(message.author.id)]
                await message.channel.send(f"✅ Your linked Quaver ID:\n{quaver_id}")
                return
            else:
                await message.channel.send("❌ **Please enter a Quaver username**, e.g.: `!quaver Cookiezi`")
                return
        else:
            username = parts[1]

        try:
            response = requests.get(API_URL_SEARCH + username)
            response.raise_for_status()
            data = response.json()
            
            if data.get("users"):
                user = data["users"][0]
                quaver_id = user["id"]
                # 儲存最後查詢的 Quaver ID
                last_searched_id[str(message.author.id)] = quaver_id
                await message.channel.send(f"✅ **{username}**'s Quaver ID:\n{quaver_id}")
            else:
                await message.channel.send(f"❌ Couldn't find Quaver stats for **{username}**")
        except requests.exceptions.RequestException as e:
            await message.channel.send("❌ API request failed, please try again later")
            print(f"API Error: {e}")

client.run(TOKEN)