"""
This script is designed to scrape data from the Steam store website for games matching the "roguelike" search term and save the scraped data to a CSV file. It then updates a SQLite database with the scraped data.

The script starts by getting the total number of pages of search results and then loops through each page, scraping game data from each search result. The function applies some filters to avoid scraping irrelevant data, such as games containing certain keywords. The function also performs numerical date conversions and validates date strings to ensure that only valid data is saved to the CSV file.

The data is then saved to a CSV file and read from the CSV file to update a SQLite database. The script checks if the game already exists in the database and inserts a new record if it doesn't exist, or updates the record if it does exist.

Overall, this script automates the process of scraping game data from the Steam store website, and enables the user to easily update a database with the scraped data.

Author: Keegan Brunmeier 2023
"""
import csv
import sqlite3
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os


# construct file paths based on current directory
db_path = os.path.join('/home/kbru/RogueLists/capvenv/roguelists', 'db.sqlite3')
csv_path = os.path.join('/home/kbru/RogueLists/capvenv/roguelists', 'roguelike.csv')

# Initialize key variables
link = 'https://store.steampowered.com/search/results'
game = 'roguelike'
head = {'cookie': 'sessionid=cd46137aee87759ca68f1347'}
blacklistlower = ['bundle', 'demo', 'soundtrack', 'dlc', 'sound track', ' pack', 'double xp', 'triple xp', 'double money', 'triple money', 'audiobook', 'coming soon', 'to be announced', 'free demo', 'free trial', 'game assets', '- skin', 'bonus content', 'skill upgrade', 'unlock all', 'skins']

def get_pagination():
  """
  Returns the total number of pages of search results for the given game term.

  :return: The total number of pages of search results.
  """
  total_item = 1

  # Set up the initial request parameters.
  param = {
    'term': game,
    'page': 1,
  }

  # Send a request to the Steam search page and parse the HTML response.
  req = requests.get(link, headers=head, params=param)
  soup = BeautifulSoup(req.text, 'html.parser')

  # Find the pagination links on the search results page.
  page_item = soup.find('div', 'search_pagination_right').find_all('a')

  # Attempt to extract the total number of pages from the pagination links.
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

def convert_release_date(release):
  """
  Convert a Steam release date string to a standardized format.

  :param release: The release date string to convert.
  :return: The converted release date string in the format 'YYYY-MM-DD', or None if the input was not valid.
  """
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

  #Invalid Date strings
  else:
    release = None

  return release

def scrapeData():
  """
  This function scrapes data from the Steam store website for games matching the 'roguelike' search term,
  and saves the scraped data to a CSV file. The function starts by getting the total number of pages of search results,
  then loops through each page, scraping game data from each search result. The function applies some filters to avoid
  scraping irrelevant data, such as games containing certain keywords. The function also performs numerical date conversions
  and validates date strings to ensure that only valid data is saved to the CSV file. Finally, the function saves the scraped
  data to a CSV file.

  Function arguments: None

  Returns: None
  """

  # Initialize variables
  count = 0
  datas = []
  checkedApps = []

  # This loop iterates over the pages of search results, using the get_pagination() function to determine the total number of pages. The loop uses the requests module to send an HTTP GET request to the Steam website for each search result page. If a timeout occurs, the function waits for 60 seconds before retrying.
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

    # Extract the game data from each search result page using BeautifulSoup to parse the HTML content. If the content cannot be extracted, the loop increments the count and continues to the next iteration.
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

      # Extract the game data for each game from the search results. The loop extracts the game's URL, app ID, tags, and title. It applies some filters to exclude games containing certain keywords (in this case, 'bundle' and 'OST'). If the game has already been scanned (as tracked by the checkedApps list), it skips that game and continues to the next iteration.
      try:
        # Check if the game is discounted and extract the necessary price elements accordingly.
        discount_block = i.find('div', 'discount_block search_discount_block')
        if discount_block:
            discount_pct = discount_block.find('div', 'discount_pct').text.strip()
            original_price = discount_block.find('div', 'discount_original_price').text.strip()
            discounted_price = discount_block.find('div', 'discount_final_price').text.strip()
            activeDiscount = True
        else:
            original_price = i.find('div', 'col search_price responsive_secondrow').text.strip()
            discounted_price = original_price
            activeDiscount = False
      except Exception:
        continue

      if original_price == '' or 'free' in original_price.lower():
        original_price = '$0.00'
        # Convert prices to floats.
      original_price = original_price.replace(',', '')[1:]
      discounted_price = discounted_price.replace(',', '')[1:]

      if 'demo' in title.lower():
        count += 1
        continue

      release = i.find('div', 'col search_released responsive_secondrow').text
      if release == '':
        count += 1
        continue

      for word in blacklistlower:
        if word in release.lower() or word in title.lower():
          skipEntry = True

      if skipEntry:
        count += 1
        continue

      # Converts the release date string to a standardized date format using the convert_release_date() function, and validates the date string to ensure that only valid data is saved to the CSV file.
      release = convert_release_date(release)
      if release is None:
        count += 1
        continue

      #"Invalid Date strings"
      if release[4] != "-" and release[7] != "-":
        count += 1
        continue

      # Replaces any commas in the game title and tag IDs with an em dash and a vertical bar, respectively, to avoid issues when saving the data to a CSV file.
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
          'base_price': original_price,
          'current_price': discounted_price,
          'release_date': release,
          'genres': tagids,
        }
      else:
        data = {
          'steam_id' : appId,
          'game_title': title,
          'base_price': original_price,
          'current_price': original_price,
          'release_date': release,
          'genres': tagids,
        }
      datas.append(data)

      count += 1
      print(f'{count}. {title}. released: {release}. price: {original_price} . link: {url}')

  df = pd.DataFrame(datas)

  # Saves the scraped data to a CSV file using the Pandas library
  df.to_csv(csv_path, index=False, header=False)
  print('all data was created')


def updateGames():
  """
  This function updates the game records in the SQLite database by reading data from the CSV file generated by the scrapeData() function.
  The function starts by creating a connection to the database and creating the Game table if it does not exist. The CSV file is then read,
  and each row is processed by extracting the relevant data and checking if the game already exists in the database. If the game exists,
  its record is updated, and if not, a new record is inserted. Finally, the function commits the changes to the database and closes the connection.

  Function arguments: None

  Returns: None
  """

  # Connect to the database
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
      if row[3] == 'ree':
        current_price = 0
      else:
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
  """
  This function calls the other functions needed to run the rogue-like Steam game scraper.
  It first calls get_pagination() to get the total number of pages of search results for the given search term.
  It then calls scrapeData() to scrape game data from each search result and save it to a CSV file.
  Finally, it calls updateGames() to insert new records or update existing records in the SQLite database.

  Function arguments: None

  Returns: None
  """
  get_pagination()
  scrapeData()
  updateGames()

run()
