import discord
import requests

API_URL_SEARCH = "https://api.quavergame.com/v2/user/search/"  # + username
API_URL_FULL = "https://api.quavergame.com/v2/user/"  # + id


async def handle_quaver_command(message, user_mappings, last_searched_id):
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
                    color=discord.Color.blue(),
                )
                if avatar_url:
                    embed.set_thumbnail(url=avatar_url)
                await message.channel.send(embed=embed)
            except requests.exceptions.RequestException as e:
                embed = discord.Embed(
                    title="❌ API error",
                    description="API request failed, please try again later",
                    color=discord.Color.red(),
                )
                await message.channel.send(embed=embed)
                print(f"API Error: {e}")
        else:
            embed = discord.Embed(
                title="❌ Missing parameter",
                description="Please enter a Quaver username, for example: `!quaver Cookiezi`",
                color=discord.Color.red(),
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
                    color=discord.Color.blue(),
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
                    color=discord.Color.red(),
                )
                await message.channel.send(embed=embed)
        except requests.exceptions.RequestException as e:
            embed = discord.Embed(
                title="❌ API error",
                description="API request failed, please try again later",
                color=discord.Color.red(),
            )
            await message.channel.send(embed=embed)
            print(f"API Error: {e}")
