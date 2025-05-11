import discord
import os
import requests
from dotenv import load_dotenv
from user import load_user_mappings, save_user_mappings
from quaver import handle_quaver_command
from rc import handle_rc_command


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
        user_id = user_mappings.get(str(message.author.id))
        await handle_rc_command(message, user_id, mode=2)


if __name__ == "__main__":
    load_dotenv()

    TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    if TOKEN:
        print("✅ Token successfully loaded")
    else:
        print("❌ Token failed to load, please check .env file")

    user_mappings = load_user_mappings()
    last_searched_id = {}

    client.run(TOKEN)
