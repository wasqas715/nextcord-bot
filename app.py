import nextcord
from nextcord import SelectOption
from nextcord.ui import Button, View, Select
import random
import os
import requests
import numpy as np
import json
from nextcord.ext import commands
from bs4 import BeautifulSoup
from yahoo_fin import stock_info as si
import string
import datetime 
import brooklyn_module as bk

from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('./.env')
load_dotenv(dotenv_path=dotenv_path)

# functionality
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('GUILD')

activity = nextcord.Game(name=f"Human Simulator")
intents = nextcord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', activity=activity, intents = intents)
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)     AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
header_apex = {
    'Accept': 'application/json',
    'Accept-Encoding': 'gzip',
    'TRN-Api-Key': '8d7c7047-d87e-410b-98d1-767d9f19d43b'
    }
    
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

# Blackjack within one embed
@bot.slash_command(description='No Hookers Included :(')
async def bj(interaction: nextcord.Interaction):
    # Shuffles deck of card, deals 2 cards to player and dealer, calcs hand vals
    # readable joins the tuple together
    cards = bk.Blackjack.generate_cards()
    your_hand, cards = bk.Blackjack.deal2(cards)
    dealer_hand, cards = bk.Blackjack.deal2(cards)
    your_hand_val = bk.Blackjack.get_hand_val(your_hand)
    dealer_hand_val = bk.Blackjack.get_hand_val(dealer_hand)
    readable_hand = bk.Blackjack.read(your_hand)
 
    # checks for BJ and adjusts fstring for return line
    temp_string = bk.Blackjack.bj_check(your_hand_val, dealer_hand_val, dealer_hand)

    async def hit_callback(interaction):
        # vars
        nonlocal cards, your_hand, your_hand_val
        # Hit
        your_hand, your_hand_val, cards = bk.Blackjack.hit_me(your_hand, cards)
        # Clean up hands
        readable_hand = bk.Blackjack.read(your_hand)
        # Result checks if 21, bust, or returns 'hit or stay'
        result_hit = bk.Blackjack.hit_bust_check(your_hand_val, dealer_hand_val)
        # Embed Form
        embedVar = nextcord.Embed(title='BlackJack', description= 'Provided by Br00k :lock:', color=0x00ff00)
        embedVar.add_field(name=f"Your Hand :rocket: {your_hand_val}", value= readable_hand, inline= False)
        embedVar.add_field(name="Dealers hand :house:", value= dealer_hand[0], inline= False)
        embedVar.add_field(name="Result:", value= result_hit, inline= False)
        await interaction.response.edit_message(embed=embedVar, view=response)

    async def stay_callback(interaction):
        # vars
        nonlocal cards, dealer_hand, dealer_hand_val, your_hand, your_hand_val
        # Dealer hits until 16
        while dealer_hand_val < 16:
            dealer_hand, dealer_hand_val, cards = bk.Blackjack.hit_me(dealer_hand, cards)
        # Clean up hands
        readable_dealer_hand = bk.Blackjack.read(dealer_hand)
        readable_hand = bk.Blackjack.read(your_hand)
        # Determine winner
        under = bk.Blackjack.winner_check(your_hand_val, dealer_hand_val)
        # Embed form
        embedVar = nextcord.Embed(title='BlackJack', description= 'Provided by Br00k :lock:', color=0x00ff00)
        embedVar.add_field(name=f"Your Hand :rocket: {your_hand_val}", value= readable_hand, inline= False)
        embedVar.add_field(name=f"Dealers hand :house: {dealer_hand_val}", value= readable_dealer_hand, inline= False)
        embedVar.add_field(name="Result", value= f"{under}", inline= False)
        await interaction.response.edit_message(embed=embedVar, view=response_blank)

    async def double_callback(interaction):
        # vars
        nonlocal cards, your_hand, your_hand_val, dealer_hand, dealer_hand_val
        # Hit
        your_hand, your_hand_val, cards = bk.Blackjack.hit_me(your_hand, cards)
        # Dealer hits until 16
        while dealer_hand_val < 16:
            dealer_hand, dealer_hand_val, cards = bk.Blackjack.hit_me(dealer_hand, cards)
        # Clean up hands
        readable_dealer_hand = bk.Blackjack.read(dealer_hand)
        readable_hand = bk.Blackjack.read(your_hand)
        # Result winner check
        result_hit = bk.Blackjack.winner_check(your_hand_val, dealer_hand_val)

        embedVar = nextcord.Embed(title='BlackJack', description= 'Provided by Br00k :lock:', color=0x00ff00)
        embedVar.add_field(name=f"Your Hand :rocket: {your_hand_val}", value= readable_hand, inline= False)
        embedVar.add_field(name=f"Dealers hand :house: {dealer_hand_val}", value= readable_dealer_hand, inline= False)
        embedVar.add_field(name="Result:", value= result_hit, inline= False)
        await interaction.response.edit_message(embed=embedVar, view=response_blank)
    
    stay_button = Button(label='Stay', style=nextcord.ButtonStyle.success)
    hit_button = Button(label='Hit', style=nextcord.ButtonStyle.danger)
    double_button = Button(label='Double', style=nextcord.ButtonStyle.secondary)

    stay_button.callback = stay_callback
    hit_button.callback = hit_callback
    double_button.callback = double_callback

    response_blank = View(timeout=60)

    response = View(timeout=60)
    response.add_item(stay_button)
    response.add_item(hit_button)

    response_first = View(timeout=60)
    response_first.add_item(stay_button)
    response_first.add_item(hit_button)
    response_first.add_item(double_button)

    embedVar = nextcord.Embed(title='BlackJack', description= 'Provided by Br00k :lock:', color=0x00ff00)
    embedVar.add_field(name=f"Your Hand :black_joker: {your_hand_val}", value= readable_hand, inline= False)
    embedVar.add_field(name="Dealers hand :house:", value= dealer_hand[0], inline= False)
    embedVar.add_field(name="Result:  ", value= temp_string, inline= False)
    await interaction.response.send_message(embed=embedVar, view=response_first)

# Grabs daily RL shop items and uses time to get the current ones
@bot.slash_command(description='See whats in RL Item Shop')
async def rlitems(interaction: nextcord.Interaction):
    response = bk.get_rlitems()
    await interaction.response.send_message(response)

# Gif of wen
@bot.slash_command(description='Get an update on how soon is wen')
async def wen(interaction: nextcord.Interaction):
    response = bk.get_wen()
    await interaction.response.send_message(response)

# randint(1,999) if n % 2 == 0 then heads, else tails
@bot.slash_command(description='Flip a high quality half dollar coin')
async def coin(interaction: nextcord.Interaction):
    response = bk.flipcoin()
    await interaction.response.send_message(response)

# Kayne West Quote API
@bot.slash_command(description='Random Kayne West Quote')
async def kanye(interaction: nextcord.Interaction):
    response = bk.get_kanye()
    await interaction.response.send_message(response)

# Currency Converter
class Dropdown_convert(nextcord.ui.Select):
    def __init__(self):
        selectOptions = [
            nextcord.SelectOption(label='Euro', description="EU"),
            nextcord.SelectOption(label='Pound', description="GBP"),
            nextcord.SelectOption(label='Franc', description="CHF"),
            nextcord.SelectOption(label='Canadian', description="CAD"),
            nextcord.SelectOption(label='Kuwaiti', description="KWD")
        ]
        super().__init__(placeholder='Which currency would you like to convert?', min_values=1, max_values=1, options=selectOptions)

    async def callback(self, interaction: nextcord.Interaction):
        temp = bk.convertcurrency()
        if self.values[0] == 'Euro':
            em = nextcord.Embed()
            em.set_author(name='USD to Euro')
            em.add_field(name='Exchange Rate', value= {temp['EUR']}, inline = True)
            await interaction.response.edit_message(embed=em)
        if self.values[0] == 'Pound':
            em = nextcord.Embed()
            em.set_author(name='USD to GBP')
            em.add_field(name='Exchange Rate', value= {temp['GBP']}, inline = True)
            await interaction.response.edit_message(embed=em)
        if self.values[0] == 'Franc':
            em = nextcord.Embed()
            em.set_author(name='USD to CHF')
            em.add_field(name='Exchange Rate', value= {temp['CHF']}, inline = True)
            await interaction.response.edit_message(embed=em)
        if self.values[0] == 'Canadian':
            em = nextcord.Embed()
            em.set_author(name='USD to CAD')
            em.add_field(name='Exchange Rate', value= {temp['CAD']}, inline = True)
            await interaction.response.edit_message(embed=em)
        if self.values[0] == 'Kuwaiti':
            em = nextcord.Embed()
            em.set_author(name='USD to KWD')
            em.add_field(name='Exchange Rate', value= {temp['KWD']}, inline = True)
            await interaction.response.edit_message(embed=em)

class Dropdown_convertView(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(Dropdown_convert())

@bot.slash_command(description='Get Currency Prices')
async def conv(ctx):
    view = Dropdown_convertView()
    await ctx.send("Br00k's Currency Exchange", view=view)

# Ping
@bot.slash_command(description='Check Latency of Bot')
async def ping(interaction: nextcord.Interaction):
    response = f'My ping is {round(bot.latency, 4) * 1000}ms!'
    await interaction.response.send_message(response)

# Zen Quote API
@bot.slash_command(description='Random Zen Quote')
async def quote(interaction: nextcord.Interaction):
    response = bk.get_quote()
    await interaction.response.send_message(response)

# Rolls two dice and gives higher of the two
@bot.slash_command(description='Roll With Advatange')
async def rwa(interaction: nextcord.Interaction):
    response = bk.rwa()
    await interaction.response.send_message(response)

# Creates PW based on length and y/n of special characters
@bot.slash_command(description='Generate a random string for a password')
async def pw(interaction: nextcord.Interaction, length: int, special_characters):
    response = bk.pw_gen(length, special_characters)
    await interaction.response.send_message(response)

# library error but should replace
# Gets volume and price of stock
@bot.slash_command(description='Get Current Price of Stock Ticker')
async def stonks(interaction: nextcord.Interaction, company_name):
    embedVar = nextcord.Embed(title=f"5 Day Chart for {company_name}", description= 'Provided by Yahoo :chart_with_upwards_trend:', color=0x00ff00, url='https://finance.yahoo.com/quote/{}/chart?p={}'.format(company_name, company_name))
    stonksdict = bk.get_stocks(company_name)
    embedVar.add_field(name="Price :rocket:", value= stonksdict['rounded_price'], inline=True)
    embedVar.add_field(name="Volume :bar_chart:", value= stonksdict['rounded_volume'], inline= False)
    await interaction.response.send_message(embed=embedVar)

# Gets current price of crypto from coingecko
@bot.slash_command(description='Get Current Price and 24h Change of Crypto')
async def crypto(interaction: nextcord.Interaction, token_name):
    embedVar = nextcord.Embed(title=f"5 Day Chart for {token_name}", description= 'Provided by CoinGekco :chart_with_upwards_trend:', color=0x00ff00, url='https://www.coingecko.com/en/coins/{}'.format(token_name))
    coindict = bk.get_coin(token_name)
    embedVar.add_field(name="Price :rocket:", value= coindict['rounded_usd'], inline= False)
    embedVar.add_field(name="24h Change % :bar_chart:", value= coindict['rounded_change'], inline= False)
    await interaction.response.send_message(embed=embedVar)

# Googles the weather for you
@bot.slash_command(description='Weather forecast')
async def weather(interaction: nextcord.Interaction, city_name):
    weather_dict = bk.get_weather(city_name)
    embedVar = nextcord.Embed(title=weather_dict['location'], description= 'Provided by Google :lock:', color=0x00ff00)
    embedVar.add_field(name="Time :rocket:", value= weather_dict['time'], inline= False)
    embedVar.add_field(name="Weather :chart_with_upwards_trend:", value= weather_dict['weather'], inline= True)
    embedVar.add_field(name="Info :eyes:", value= weather_dict['info'], inline= True)
    embedVar.add_field(name="Wind :dodo:", value= weather_dict['wind'], inline= True)
    await interaction.response.send_message(embed=embedVar)

# Gets current Apex Legends stats
@bot.slash_command(description='Get Current Apex Rank')
async def apex(interaction: nextcord.Interaction, gamertag):
    username = gamertag.replace(" ", "%20")
    apexdict = bk.get_apex(gamertag)
    embedVar = nextcord.Embed(title=f"{gamertag} as {apexdict['legend']} LVL {apexdict['level']}", description= 'Provided by Apex :chart_with_upwards_trend:', color=0x00ff00)
    embedVar.add_field(name="BR Rank :rocket:", value= apexdict['br_rank'], inline=True)
    embedVar.add_field(name="BR Level :bar_chart:", value= apexdict['br_level'], inline= True)
    embedVar.add_field(name="Arena Rank :rocket:", value= apexdict['arena_rank'], inline=True)
    embedVar.add_field(name="Arena Level :bar_chart:", value= apexdict['arena_level'], inline= True)
    await interaction.response.send_message(embed=embedVar)


'''
# Remove RL command as selenium and docker are a bad combo
@bot.slash_command(description='Get RL Rank of someone else')
async def rl(interaction: nextcord.Interaction, gamertag, hardware: str = nextcord.SlashOption(
        name="picker",
        choices={"Xbox": 'xbl', "Epic": 'epic', "Playstation": 'psn', 'Switch': 'switch' },
                        ),
            ):
    await interaction.response.defer(with_message=True,ephemeral=True)
    username = gamertag.replace(" ", "%20")
    rldict = bk.get_rl(gamertag, hardware)
    embedVar = nextcord.Embed(title=f"{gamertag}", description= 'Provided by TRN :chart_with_upwards_trend:', color=0x00ff00)
    embedVar.add_field(name="1v1 Rank :repeat_one:", value= rldict['ones'], inline=True)
    embedVar.add_field(name="2v2s Level :two:", value= rldict['twos'], inline= True)
    embedVar.add_field(name="3v3s Rank :three:", value= rldict['threes'], inline=True)
    embedVar.add_field(name="Tournament Rank :crown:", value= rldict['tournament'], inline= True)
    await interaction.followup.send(embed=embedVar)
'''

bot.run(TOKEN)
