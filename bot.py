import discord
import requests
import json
import os
from dotenv import load_dotenv  # 載入 .env 檔案

# 載入 .env 檔案
load_dotenv()

# 輸出確認 Token 是否成功載入
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
# if TOKEN:
    # print("✅ Token 成功載入")
# else:
    # print("❌ Token 未成功載入，請檢查 .env 檔案")


# 載入環境變數
API_URL_SEARCH = "https://api.quavergame.com/v1/users/search/"
API_URL_FULL = "https://api.quavergame.com/v1/users/full/"
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

# 啟用 message_content 權限
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ Bot 已登入為 {client.user}')

@client.event
async def on_message(message):
    print(f"收到訊息: {message.content}")  # 調試輸出

    if message.author == client.user:
        return

    if message.content.startswith("!link"):
        parts = message.content.split(" ")
        if len(parts) < 2:
            await message.channel.send("❌ **請輸入 Quaver 使用者名稱**，例如： `!link Cookiezi`")
            return

        username = parts[1]
        user_mappings[str(message.author.id)] = username
        save_user_mappings(user_mappings)
        await message.channel.send(f"✅ **{message.author.name}** 已連結到 Quaver 使用者 **{username}**")
        return

    if message.content.startswith("!unlink"):
        if str(message.author.id) in user_mappings:
            del user_mappings[str(message.author.id)]
            save_user_mappings(user_mappings)
            await message.channel.send(f"✅ **{message.author.name}** 已解除 Quaver 使用者連結")
        else:
            await message.channel.send("❌ **您尚未連結 Quaver 使用者**")
        return

    if message.content.startswith("!quaver"):
        print(f"指令：!quaver 被觸發")  # 調試輸出
        parts = message.content.split(" ")
        if len(parts) < 2:
            if str(message.author.id) in user_mappings:
                username = user_mappings[str(message.author.id)]
            else:
                await message.channel.send("❌ **請輸入 Quaver 使用者名稱**，例如： `!quaver Cookiezi`")
                return
        else:
            username = parts[1]

        response = requests.get(API_URL + username)

        if response.status_code == 200:
            data = response.json()
            if data["users"]:
                user = data["users"][0]
                # rank = user["global_rank"]
                id = user["id"]
                # pp = user["pp"]
                await message.channel.send(f"✅ **{username}** 的 Quaver id：\n{id}")
            else:
                await message.channel.send(f"❌ 找不到 **{username}** 的 Quaver 成績")
        else:
            await message.channel.send("❌ API 請求失敗，請稍後再試")

# 讓 Bot 上線
client.run(TOKEN)
