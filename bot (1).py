import discord
import os
import aiohttp
import asyncio
from discord.ext import commands, tasks
from dotenv import load_dotenv
from datetime import time
from bs4 import BeautifulSoup
import requests
import json
import csv

load_dotenv()

DISCORD_TOKEN = os.getenv("BOT_TOKEN")
CHECK_INTERVAL = 600
urls = [os.getenv("SITE_ONE"), os.getenv("SITE_TWO"), os.getenv("SITE_THREE"), os.getenv("SITE_FOUR"), os.getenv("SITE_FIVE")]
divs = [os.getenv("DIV_ONE"), os.getenv("DIV_TWO"), os.getenv("DIV_THREE"), os.getenv("DIV_FOUR"), os.getenv("DIV_FIVE")]
div_types = [os.getenv("DIV_TYPE_ONE"), os.getenv("DIV_TYPE_TWO"), os.getenv("DIV_TYPE_THREE"), os.getenv("DIV_TYPE_FOUR"), os.getenv("DIV_TYPE_FIVE")]
titles = [os.getenv("TITLE_ONE"), os.getenv("TITLE_TWO"), os.getenv("TITLE_THREE"), os.getenv("TITLE_FOUR"), os.getenv("TITLE_FIVE")]
title_types = [os.getenv("TITLE_TYPE_ONE"), os.getenv("TITLE_TYPE_TWO"), os.getenv("TITLE_TYPE_THREE"), os.getenv("TITLE_TYPE_FOUR"), os.getenv("TITLE_TYPE_FIVE")]
links = [os.getenv("LINK_ONE"), os.getenv("LINK_TWO"), os.getenv("LINK_THRE"), os.getenv("LINK_FOUR"), os.getenv("LINK_FIVE")]
files = [os.getenv("STATE_FILE_ONE"), os.getenv("STATE_FILE_TWO"), os.getenv("STATE_FILE_THREE"), os.getenv("STATE_FILE_FOUR"), os.getenv("STATE_FILE_FIVE")]
prefixes = [os.getenv("PREFIX_ONE"), os.getenv("PREFIX_TWO"), os.getenv("PREFIX_THREE"), os.getenv("PREFIX_FOUR"), os.getenv("PREFIX_FIVE")]

intents = discord.Intents.all()
intents.message_content = True
intents.slash_commands = True
bot = commands.Bot(command_prefix='/', intents=intents)

def load_state(i):
    if os.path.exists(files[i]):
        try:
            with open(files[i], 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    return {"latest_title": ""}

def save_state(title,i):
    state = {"latest_title": title}
    with open(files[i], 'w') as f:
        json.dump(state, f)

def make_embed(title,url,i):
    embed = discord.Embed(title = "New article posted", color = discord.Colour.from_rgb(244, 184, 22))
    embed.add_field(name="", value="**[" + title + "](" + url + ")**", inline=False)
    if(i <= 3):
        embed.add_field(name="", value="<:coin_desk:1523075786519875615>*CoinDesk*", inline=False)
    else:
        embed.add_field(name="", value="<:coin_telegraph:1523065950751162458>*CoinTelegraph*", inline=False)
    embed.add_field(name="", value="-# service brought to you by ffwm")
    return embed
    
@tasks.loop(seconds=CHECK_INTERVAL)
async def check_articles():
    async with aiohttp.ClientSession() as session:
        for i in range(len(urls)):
            try:
                state = await asyncio.to_thread(load_state, i)

                async with session.get(urls[i]) as response:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    latest_div = soup.find(div_types[i], class_=divs[i])
                    if not latest_div:
                        continue
                    current_title = latest_div.find(title_types[i], class_=titles[i]).get_text(strip=True)

                    if current_title != state.get('latest_title', ''):
                        link = latest_div.find('a', class_=links[i])
                        if not link:
                            continue
                        url = link.get('href')
                        url = prefixes[i] + url
                        print(f"New article found: {current_title} ({url})")
                        embed=make_embed(current_title,url,i)
                        channel = bot.get_channel(1463289640524972034)
                        await channel.send(content = "<@&1464610989163937843>",embed=embed)
                        await asyncio.to_thread(save_state, current_title, i)
                    else:
                        print(f"No new article for URL {i}")
            except Exception as e:
                print(f"Error checking URL {i}: {e}")

@bot.command
async def add_alert():
    

# configures the bot when online
@bot.event
async def on_ready():
    activity = discord.Activity(type=discord.ActivityType.watching, name="Web3 Actuality")
    await bot.change_presence(status=discord.Status.idle, activity=activity)

    if not check_articles.is_running():
        check_articles.start()  # Start the task if it's not already started
    print(f'Bot is online as {bot.user}')

bot.run(DISCORD_TOKEN)