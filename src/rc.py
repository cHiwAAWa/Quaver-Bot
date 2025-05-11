import discord
import requests


async def handle_rc_command(message, user_id, mode=2):
    # https://api.quavergame.com/v2/user/:id/scores/:mode/recent
    response = requests.get(f"https://api.quavergame.com/v2/user/{user_id}/scores/{mode}/recent")
    print(response.url)
    if response.status_code != 200:
        embed = discord.Embed(
            title="❌ API error",
            description="API request failed, please try again later",
            color=discord.Color.red(),
        )
        await message.channel.send(embed=embed)
        print(f"API Error: {response.status_code}")
        return
    print(response)
    # Example placeholder for the !rc command
    embed = discord.Embed(
        title=response.json().get("title", "Recent Scores"),
        description=response.json().get("description", "No description available"),
        color=discord.Color.blue(),
    )
    await message.channel.send(embed=embed)
