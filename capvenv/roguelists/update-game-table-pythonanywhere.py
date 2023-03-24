import csv
import sqlite3
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

import os

# construct file paths based on current directory
db_path = os.path.join(os.getcwd(), 'db.sqlite3')
csv_path = os.path.join(os.getcwd(), 'roguelike.csv')

link = 'https://store.steampowered.com/search/results'
# game = input('Enter game search: ')
game = 'roguelike'
head = {'cookie': 'sessionid=cd46137aee87759ca68f1347'}
blacklistlower = ['bundle', 'demo', 'soundtrack', 'dlc', 'sound track', ' pack', 'double xp', 'triple xp', 'double money', 'triple money', 'audiobook', 'coming soon', 'to be announced', 'free demo', 'free trial', 'game assets', '- skin', 'bonus content', 'skill upgrade', 'unlock all', 'skins']

checkedApps = []
dataset = []

# try:
#   os.mkdir('resultfile')
# except FileExistsError:
#   pass


def get_pagination():
  total_item = 1
  param = {
    'term': game,
    'page': 1,
  }

  req = requests.get(link, headers=head, params=param)
  soup = BeautifulSoup(req.text, 'html.parser')
  page_item = soup.find('div', 'search_pagination_right').find_all('a')

  try:
    total_item = int(page_item[4].text)
  except Exception:
    pass
    try:
      total_item = int(page_item[3].text)
    except Exception:
      pass
      try:
        total_item = int(page_item[2].text)
      except Exception:
        pass
        try:
          total_item = int(page_item[1].text)
        except Exception:
          pass
          try:
            total_item = int(page_item[0].text)
          except Exception:
            pass
  return 1 + total_item


def scrap():
  count = 0
  datas = []

  for j in range(1, get_pagination()):
    param = {
      'term': game,
      'page': j,
    }
    try:
      req = requests.get(link, params=param, headers=head)
    except:
      print("Timeout, waiting 1 minute...")
      time.sleep(60)
      req = requests.get(link, params=param, headers=head)
    soup = BeautifulSoup(req.text, 'html.parser')

    try:
      content = soup.find('div', {'id': 'search_resultsRows'}).find_all('a')
    except AttributeError:
      count += 1
      continue
    for i in content:
      activeDiscount = False
      skipEntry = False
      url = i['href']
      if 'bundle' in url:
        count += 1
        continue
      try:
        appId = i['data-ds-appid']
      except KeyError:
        count += 1
        continue
      if appId in checkedApps:
        count += 1
        print("APP ALREADY SCANNED")
        continue
      try:
        tagids = i['data-ds-tagids']
      except KeyError:
        count += 1
        continue
      checkedApps.append(appId)
      title = i.find('div', 'col search_name ellipsis').text.strip().replace('\n', ' ')
      
      if 'OST' in title:
        count += 1
        continue

      try:
        price = i.find('div', 'col search_price responsive_secondrow').text.strip()
      except Exception:
        activeDiscount = True
        price = i.find('span', {'style': 'color: #888888;'}).text             
        discountedPrice = i.find('div', 'col search_price discounted responsive_secondrow').find('br').next_sibling.strip()
        
      if price == '' or 'free' in price.lower():
        price = '$0.00'

      if 'demo' in title.lower():
        count += 1
        continue
      
      release = i.find('div', 'col search_released responsive_secondrow').text
      if release == '':
        count += 1
        continue
      
      for word in blacklistlower:
        if word in release.lower() or word in title.lower() or word in price.lower():
          skipEntry = True
          
      if skipEntry:
        count += 1
        continue
      
      #Numerical Date Conversions
      #"Jul 8, 2023"
      if len(release) == 11 or len(release) == 12:
        if release[-4:-2] == "20":
          if release[5] == "," or release[6] == ",":
            release = datetime.strptime(release, '%b %d, %Y')
            release = release.strftime('%Y-%m-%d')
      #"2023"    
      elif len(release) == 4:
        if release[0:2] == "20":
          release = f"{release}-12-31"
      #"Q2 2026"
      elif release[0] == 'Q':
        if len(release) == 7:
          qConvertMonth = (int(release[1]) * 3)
          qConvertYear = release[-4:]
          release = f"{qConvertMonth} {qConvertYear}"
          release = datetime.strptime(release, '%m %Y')
          release = release.strftime('%Y-%m-%d')
      #"November 2021"
      elif release[5] != "," and release[6] != ",":
        if release[-4:-2] == "20":
          if release[0] != "Q":
            if release[3] != " " and release[0:3] != "May":
              if len(release) != 4:
                release = datetime.strptime(release, '%B %Y')
                release = release.strftime('%Y-%m-%d')
      #"Mar 2022"
      elif len(release) == 8:
        if release[-4:-2] == "20":
          if release[3] == " ":
            release = datetime.strptime(release, '%b %Y')
            release = release.strftime('%Y-%m-%d')
      #"Invalid Date strings"
      if release[4] != "-" and release[7] != "-":
        count += 1
        continue
      
      #For CSV
      if "," in title:
        title = title.replace(",", " —")
      if "," in tagids:
        tagids = tagids.replace(",","|")
        tagids = str(tagids)
        tagids = tagids[1:-2]

      if activeDiscount:
        data = {
          'steam_id' : appId,
          'game_title': title,
          'base_price': price[1:],
          'current_price': discountedPrice[1:],
          'release_date': release,
          'genres': tagids,
        }
      else:
        data = {
          'steam_id' : appId,
          'game_title': title,
          'base_price': price[1:],
          'current_price': price[1:],
          'release_date': release,
          'genres': tagids,
        }
      datas.append(data)

      count += 1
      print(f'{count}. {title}. released: {release}. price: {price} . link: {url}')
            
  # with open(f'resultfile/json_data_{game}.json', 'w+') as outfile:
  #   json.dump(datas, outfile)

  df = pd.DataFrame(datas)
  df.to_csv(csv_path, index=False, header=False)
  print('all data was created')


def updateGames():
  # connect to the database
  conn = sqlite3.connect(db_path)
  print(conn)
  c = conn.cursor()

  # create the Game table if it does not exist
  c.execute('''CREATE TABLE IF NOT EXISTS rogueapp_game
              (steam_id INTEGER PRIMARY KEY,
              game_title TEXT,
              base_price REAL,
              current_price REAL,
              release_date DATE,
              genres TEXT)''')
  # read the CSV file
  with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    # next(reader) # skip the header row
    for row in reader:
      steam_id = int(row[0])
      game_title = row[1]
      base_price = float(row[2])
      current_price = float(row[3])
      release_date = datetime.strptime(row[4], '%Y-%m-%d').date()
      genres = row[5]
      
      # check if the game already exists in the database
      c.execute("SELECT COUNT(*) FROM rogueapp_game WHERE steam_id=?", (steam_id,))
      result = c.fetchone()[0]
      
      if result == 0:
        # game does not exist, insert a new record
        print(f"Inserting game {game_title} with steam_id {steam_id}")
        c.execute("INSERT INTO rogueapp_game (steam_id, game_title, base_price, current_price, release_date, genres) VALUES (?, ?, ?, ?, ?, ?)", 
                  (steam_id, game_title, base_price, current_price, release_date, genres))
      else:
        # game already exists, update the record
        print(f"Updating game {game_title} with steam_id {steam_id}")
        c.execute("UPDATE rogueapp_game SET game_title=?, base_price=?, current_price=?, release_date=?, genres=? WHERE steam_id=?", 
                  (game_title, base_price, current_price, release_date, genres, steam_id))
    conn.commit()
          
  conn.close()


def run():
  get_pagination()
  scrap()
  updateGames()


run()