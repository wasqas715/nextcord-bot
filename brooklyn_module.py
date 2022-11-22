# discord bot v2 with commands
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
import pandas as pd
# from selenium import webdriver
# from selenium.webdriver.common.by import By
import re
import pytz


#selenium stuffs
'''
options = webdriver.ChromeOptions()
options.add_argument('--ignore-ssl-errors=yes')
options.add_argument('--ignore-certificate-errors')
'''

#Headers Vars
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)     AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
header_apex = {
    'Accept': 'application/json',
    'Accept-Encoding': 'gzip',
    'TRN-Api-Key': '8d7c7047-d87e-410b-98d1-767d9f19d43b'
    }

card_values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
suits = [":clubs:", ":diamonds:", ":heart:", ":spades:"]
 
face_cards = {
    1: "A",
    11: "J",
    12: "Q",
    13: "K"
}

fc_vals = {
    "J": 10,
    "Q": 10,
    "K": 10,
    "A": (1, 11)
}
class Blackjack:
  # Create/shuffle deck
  def generate_cards():
    cards = []
    for value in card_values:
      for suit in suits:
          if value in face_cards:
              _card = (face_cards[value], suit)
          else:
              _card = (value, suit)
          cards.append(_card)
    return cards
  # input: cards -> output: removed card, and remaining cards
  def deal_card(cards):
    i = random.randint(0, len(cards)-1)
    card = cards[i]
    cards.pop(i)
    return card, cards
  # deals two cards
  def deal2(cards):
    card1, cards = Blackjack.deal_card(cards)
    card2, cards = Blackjack.deal_card(cards)
    dealt = [card1, card2]
    return dealt, cards

  def read(handy):
    temper = [(str(x), str(y)) for x, y in handy]
    reader = [' '.join(i) for i in temper]
    return reader

  def get_hand_val(hand):
    val = 0
    for card in hand:  
      if card[0] in fc_vals:
        if card[0] != 'A':
          val += fc_vals[card[0]]
        else:
          if val + fc_vals[card[0]][1] > 21:
              val += fc_vals[card[0]][0]
          else:
            val += fc_vals[card[0]][1]
      else:
        val += card[0]
    return val

  def hit_me(hand, cards):
    hit, cards = Blackjack.deal_card(cards)
    hand.append(hit)
    new_hand_val = Blackjack.get_hand_val(hand)
    return hand, new_hand_val, cards

  def bj_check(your_hand_val, dealer_hand_val, dealer_hand):
    if your_hand_val == 21:
        temp_string = f'Blackjack!'
    elif dealer_hand_val == 21:
        temp_string = f'Dealer Blackjack Dealer'
    else: 
        temp_string = 'Hit or Stay'
    return temp_string

  def winner_check(your_hand_val, dealer_hand_val):
    if your_hand_val < 21 and dealer_hand_val < 21:
      if your_hand_val > dealer_hand_val:
          under = f"You Win {your_hand_val} > {dealer_hand_val}"
      elif dealer_hand_val > your_hand_val:
          under = f"Dealer Wins {dealer_hand_val} > {your_hand_val}"
      else:
          under = f"Tie"
    elif dealer_hand_val == 21:
        under = f"Dealer Wins"
    elif your_hand_val == 21:
        under = f"You Win"
    elif your_hand_val < 21 and dealer_hand_val > 21:
        under = f"Dealer Bust"
    elif your_hand_val > 21:
        under = f"You Bust"
    else:
        under = f"Dealer Busts {dealer_hand_val} > {your_hand_val}"
    return under

  def hit_bust_check(your_hand_val, dealer_hand_val):
    if your_hand_val == 21:
        result_hit = f"You Win {your_hand_val} > {dealer_hand_val}"
    elif your_hand_val > 21:
        result_hit = f"You busted {your_hand_val} < {dealer_hand_val}"
    else:
        result_hit = "Hit or Stay"
    return result_hit

def get_weather(city_name):
  city_name = city_name+" weather"
  city_name = city_name.replace(" ","+")
  res=requests.get(f'https://www.google.com/search?q={city_name}&oq={city_name}&aqs=chrome.0.i635i39l2j0l4j46j690.6128j1j7&sourceid=chrome&ie=UTF-8',headers=headers)
  ret_dict = {}
  soup = BeautifulSoup(res.text,'html.parser')
  ret_dict['location'] = soup.select('#wob_loc')[0].getText().strip()
  ret_dict['time'] = soup.select('#wob_dts')[0].getText().strip()
  ret_dict['info'] = soup.select('#wob_dc')[0].getText().strip()
  ret_dict['weather'] = soup.select('#wob_tm')[0].getText().strip()
  ret_dict['wind'] = soup.select('#wob_ws')[0].getText().strip()
  return(ret_dict)

def get_stocks(company_name):
  stonks_dict = {}
  price = si.get_live_price(company_name)
  stonks_dict['rounded_price'] = float(np.round(price, 2))
  volume = si.get_quote_table(company_name)['Volume']
  stonks_dict['rounded_volume'] = float(np.round(volume, 0))
  return(stonks_dict)

def get_coin(tokenname):
  response = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={tokenname}&vs_currencies=usd&include_24hr_change=true")
  json_data = json.loads(response.text)
  coin_dict = {}
  usd = json_data[f'{tokenname}']['usd']
  coin_dict['rounded_usd'] = float(np.round(usd, 5))
  usd_change = json_data[f'{tokenname}']['usd_24h_change']
  coin_dict['rounded_change'] = float(np.round(usd_change, 2))
  return(coin_dict) 

def get_quote():
  response = requests.get("https://zenquotes.io/api/random")
  json_data = json.loads(response.text)
  quote = json_data[0]['q'] + " -" + json_data[0]['a']
  return(quote)

def get_kanye():
  response = requests.get("https://api.kanye.rest")
  json_data = json.loads(response.text)
  kanye = json_data['quote'] + '- Kanye West'
  return(kanye)

def convertcurrency():
  response = requests.get("https://v6.exchangerate-api.com/v6/e2eb22ecda02962cbbd88ad4/latest/USD")
  json_data = json.loads(response.text)
  rates = json_data['conversion_rates']
  return(rates)

def pw_gen(arg, spec_char):
    pw =[]
    pw_string = ''
    arg = int(arg)
    if spec_char == 'y':
      master = string.ascii_letters + string.digits + string.punctuation 
    else:
      master = string.ascii_letters + string.digits 
    for i in range(arg):
        pw.append(random.choice(master))
    pw_string="".join(map(str,pw))
    return(pw_string)

def rwa():
    roll_one = random.randint(1,20)
    roll_two = random.randint(1,20)
    if roll_one < roll_two:
      return roll_two
    else:
      return roll_one

def get_wen():
  response = "https://c.tenor.com/HBr3xjGPM8oAAAAC/when-wen.gif"
  return response

def flipcoin():
  flip = random.randint(1,999)
  if flip % 2 == 0:
    response = "https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/US_Half_Dollar_Obverse_2015.png/220px-US_Half_Dollar_Obverse_2015.png"
    return response
  else:
    response = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/US_50_Cent_Rev.png/220px-US_50_Cent_Rev.png"
    return response

def get_rlitems():
  tz = pytz.timezone('US/Central')
  current_time = datetime.datetime.now(tz)
  if current_time.hour < 15:
    day_adjusted = current_time.day - 1
    response = f'https://rocket-league.com/content/media/itemshopPreviewDetailed/{current_time.year}-{current_time.month:02d}-{day_adjusted:02d}.jpg'
  else:
    day_adjusted = current_time.day
    response = f'https://rocket-league.com/content/media/itemshopPreviewDetailed/{current_time.year}-{current_time.month:02d}-{current_time.day:02d}.jpg'
  return(response)

def get_apex(gamertag):
  gamertag = gamertag.replace(" ", "%20")
  response = requests.get(f"https://public-api.tracker.gg/v2/apex/standard/profile/xbl/{gamertag}", headers=header_apex)
  json_data = json.loads(response.text)
  apex_dict = {}
  apex_dict['legend'] = json_data['data']['metadata']['activeLegendName']  
  apex_dict['level'] = json_data['data']['segments'][0]['stats']['level']['displayValue']
  apex_dict['br_level'] = json_data['data']['segments'][0]['stats']['rankScore']['displayValue']
  apex_dict['br_rank'] = json_data['data']['segments'][0]['stats']['rankScore']['metadata']['rankName']
  apex_dict['arena_rank'] = json_data['data']['segments'][0]['stats']['arenaRankScore']['metadata']['rankName']
  apex_dict['arena_level'] = json_data['data']['segments'][0]['stats']['arenaRankScore']['displayValue']
  return(apex_dict)

'''
def get_rl(gamertag, hardware):
  gamertag = gamertag.replace(" ", "%20")
  driver = webdriver.Remote(command_executor='http://web:4444/wd/hub',
                            options=options
                          )
  driver.maximize_window()
  # hardware = "xbl"
  tag = gamertag.replace(" ", "%20")
  url = f"https://rocketleague.tracker.network/rocket-league/profile/{hardware}/{tag.lower()}/overview"

  driver.get(url)
  driver.implicitly_wait(2) #allow some time to fully load
  ranks = driver.find_elements(By.CSS_SELECTOR, r'[class="rank"]')
  # mmr = driver.find_elements(By.CSS_SELECTOR, r'[class="mmr"]')
  basic = []
  for i in ranks:
      # if re.match(r'^[A-Za-z]', i.text):
      if re.match(r'^[SGPDCS]', i.text):
          basic.append(i.text)
      else:
          continue
  print(basic)
  rl_dict = {}
  rl_dict['ones'] = basic[0]  
  rl_dict['twos'] = basic[1]  
  rl_dict['threes'] = basic[2]  
  rl_dict['tournament'] = basic[7]
  driver.quit()  
  return(rl_dict)
'''

