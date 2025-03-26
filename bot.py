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
                    title="❌ 連結失敗",
                    description="請先使用 `!quaver` 查詢一個用戶，或直接指定 username，例如：`!link Cookiezi`",
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
                        title="❌ 用戶未找到",
                        description=f"找不到 Quaver 用戶 **{username}**",
                        color=discord.Color.red()
                    )
                    await message.channel.send(embed=embed)
                    return
            except requests.exceptions.RequestException as e:
                embed = discord.Embed(
                    title="❌ API 錯誤",
                    description="API 請求失敗，請稍後再試",
                    color=discord.Color.red()
                )
                await message.channel.send(embed=embed)
                print(f"API Error: {e}")
                return

        user_mappings[str(message.author.id)] = quaver_id
        save_user_mappings(user_mappings)
        embed = discord.Embed(
            title="✅ 連結成功",
            description=f"**{message.author.name}** 已連結到 Quaver ID **{quaver_id}**",
            color=discord.Color.green()
        )
        await message.channel.send(embed=embed)
        return

    if message.content.startswith("!unlink"):
        if str(message.author.id) in user_mappings:
            del user_mappings[str(message.author.id)]
            save_user_mappings(user_mappings)
            embed = discord.Embed(
                title="✅ 解除連結",
                description=f"**{message.author.name}** 的 Quaver 連結已解除",
                color=discord.Color.green()
            )
            await message.channel.send(embed=embed)
        else:
            embed = discord.Embed(
                title="❌ 未連結",
                description="您尚未連結任何 Quaver 用戶",
                color=discord.Color.red()
            )
            await message.channel.send(embed=embed)
        return

    if message.content.startswith("!quaver"):
        print(f"Command: !quaver triggered")
        parts = message.content.split(" ")
        if len(parts) < 2:
            if str(message.author.id) in user_mappings:
                quaver_id = user_mappings[str(message.author.id)]
                embed = discord.Embed(
                    title="✅ 已連結的 Quaver ID",
                    description=f"您的 Quaver ID：**{quaver_id}**",
                    color=discord.Color.blue()
                )
                await message.channel.send(embed=embed)
                return
            else:
                embed = discord.Embed(
                    title="❌ 缺少參數",
                    description="請輸入 Quaver 用戶名，例如：`!quaver Cookiezi`",
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
                user = data["users"][0]
                quaver_id = user["id"]
                last_searched_id[str(message.author.id)] = quaver_id
                embed = discord.Embed(
                    title=f"✅ {username} 的 Quaver 資訊",
                    description=f"Quaver ID: **{quaver_id}**",
                    color=discord.Color.blue()
                )
                embed.set_footer(text="輸入 !link 可直接連結此 ID")
                await message.channel.send(embed=embed)
            else:
                embed = discord.Embed(
                    title="❌ 用戶未找到",
                    description=f"找不到 **{username}** 的 Quaver 資料",
                    color=discord.Color.red()
                )
                await message.channel.send(embed=embed)
        except requests.exceptions.RequestException as e:
            embed = discord.Embed(
                title="❌ API 錯誤",
                description="API 請求失敗，請稍後再試",
                color=discord.Color.red()
            )
            await message.channel.send(embed=embed)
            print(f"API Error: {e}")

client.run(TOKEN)