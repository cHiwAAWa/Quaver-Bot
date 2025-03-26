import discord
import requests
import json
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Verify Token loading
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if TOKEN:
    print("✅ Token successfully loaded")
else:
    print("❌ Token failed to load, please check .env file")

# Environment variables
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

# Enable message_content permission
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ Bot logged in as {client.user}')

@client.event
async def on_message(message):
    print(f"Received message: {message.content}")  # Debug output

    if message.author == client.user:
        return

    if message.content.startswith("!link"):
        parts = message.content.split(" ")
        if len(parts) < 2:
            await message.channel.send("❌ **Please enter a Quaver username**, e.g.: `!link Cookiezi`")
            return

        username = parts[1]
        user_mappings[str(message.author.id)] = username
        save_user_mappings(user_mappings)
        await message.channel.send(f"✅ **{message.author.name}** linked to Quaver user **{username}**")
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
        print(f"Command: !quaver triggered")  # Debug output
        parts = message.content.split(" ")
        if len(parts) < 2:
            if str(message.author.id) in user_mappings:
                username = user_mappings[str(message.author.id)]
            else:
                await message.channel.send("❌ **Please enter a Quaver username**, e.g.: `!quaver Cookiezi`")
                return
        else:
            username = parts[1]

        try:
            response = requests.get(API_URL_SEARCH + username)
            response.raise_for_status()  # Raises an exception for bad status codes
            data = response.json()
            
            if data.get("users"):  # Use .get() to safely check for 'users' key
                user = data["users"][0]
                id = user["id"]
                await message.channel.send(f"✅ **{username}**'s Quaver ID:\n{id}")
            else:
                await message.channel.send(f"❌ Couldn't find Quaver stats for **{username}**")
        except requests.exceptions.RequestException as e:
            await message.channel.send("❌ API request failed, please try again later")
            print(f"API Error: {e}")  # Debug output

# Start the bot
client.run(TOKEN)