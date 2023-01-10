import pandas as pd
import os
import time
import urllib.request
import bs4 as bs
import webbrowser
from kaggle.api.kaggle_api_extended import KaggleApi
import zipfile


# 1. Sheffield Gigs (Automated)
# Open the url
source = urllib.request.urlopen('https://www.sheffieldmusicscene.co.uk/w_city_by_date_Sheffield.html').read()
soup = bs.BeautifulSoup(source,'lxml')

# Read the webpage to a pandas df
table = soup.find_all('table')
gigs = pd.read_html(str(table))[0][['Date','Event Title','Venue']]
gigs = gigs.rename(columns={"Event Title": "artist"})
gigs['Date'] = gigs['Date'].str[:10]
gigs['artist'] = gigs['artist'].str.lower()

# 2. Pitchfork Reviews
# Taken from here https://www.lamorbidamacchina.com/pitchforkscores/export.php
os.remove('Downloads/pitchfork-scores-export.csv')
webbrowser.open('https://www.lamorbidamacchina.com/pitchforkscores/export.php')
time.sleep(10)
pitchfork = pd.read_csv('Downloads/pitchfork-scores-export.csv',sep=';')[['score','author','title']]
pitchfork = pitchfork.rename(columns={"author": "artist", "title": "album"})

# Taken from here https://www.dropbox.com/s/cqf7cgxh91eoeyn/pitchfork.csv?dl=0
df_hist = pd.read_csv('Documents/GitHub/sheffgigs/Data/pitchfork.csv')[['artist','album','score']]

pitchfork = pitchfork.append(df_hist)

pitchfork = pitchfork.rename(columns={"score": "pitchfork-score"})

pitchfork['artist'] = pitchfork['artist'].str.lower()
pitchfork['album'] = pitchfork['album'].str.lower()
pitchfork['mergekey'] = pitchfork['artist']+pitchfork['album']
pitchfork = pitchfork.sort_values(by=['mergekey'], ascending=False)
pitchfork = pitchfork.drop_duplicates()


# 3. Theneedledrop Reviews
# TND Data from https://www.kaggle.com/datasets/josephgreen/anthony-fantano-album-review-dataset/code?select=albums.csv
# Authenticate kaggle api
api = KaggleApi()
api.authenticate()

# Download and upzip the kaggle file
api.dataset_download_files('josephgreen/anthony-fantano-album-review-dataset', path='Documents/GitHub/sheffgigs/Data')
with zipfile.ZipFile('Documents/GitHub/sheffgigs/Data/anthony-fantano-album-review-dataset.zip', 'r') as zipref:
    zipref.extractall('Documents/GitHub/sheffgigs/Data')

tnd = pd.read_csv('Documents/GitHub/sheffgigs/Data/albums.csv')[['project_name','artist','rating']]
tnd = tnd.rename(columns={"rating": "TND-score", "project_name": "album"})
tnd['mergekey'] = tnd['artist']+tnd['album']
tnd = tnd.sort_values(by=['mergekey'], ascending=False)
tnd = tnd.drop_duplicates()


# 4 Combine pitchfork and TND reviews
index = pitchfork.append(tnd)['mergekey'].sort_values().drop_duplicates()

reviews = pd.merge(index, pitchfork, on='mergekey', how='left')
reviews = pd.merge(reviews, tnd, on='mergekey', how='left')

reviews['artist'] = reviews.artist_x.combine_first(reviews.artist_y)
reviews['album'] = reviews.album_x.combine_first(reviews.album_y)
reviews = reviews[['artist','album','pitchfork-score','TND-score']]

# Merge the reviews to the gigs
df = pd.merge(gigs, reviews, on='artist', how='inner')
