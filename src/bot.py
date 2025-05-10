import discord
import os
import json
import requests
from dotenv import load_dotenv
from quaver import handle_quaver_command
from rc import handle_rc_command


def load_user_mappings():
    if os.path.exists(USER_MAPPINGS_FILE):
        with open(USER_MAPPINGS_FILE, "r") as file:
            return json.load(file)
    return {}


def save_user_mappings(mappings):
    with open(USER_MAPPINGS_FILE, "w") as file:
        json.dump(mappings, file)


# Define the client object here
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"✅ Bot logged in as {client.user}")
    activity = discord.Game(name="Quaver")
    await client.change_presence(status=discord.Status.online, activity=activity)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!quaver"):
        await handle_quaver_command(message, user_mappings, last_searched_id)

    if message.content.startswith("!rc"):
        await handle_rc_command(message)


if __name__ == "__main__":
    load_dotenv()

    TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    if TOKEN:
        print("✅ Token successfully loaded")
    else:
        print("❌ Token failed to load, please check .env file")

    USER_MAPPINGS_FILE = "data/user_mappings.json"

    user_mappings = load_user_mappings()
    last_searched_id = {}

    client.run(TOKEN)
