import pandas as pd
import os
import time
import urllib.request
import bs4 as bs
import webbrowser
from kaggle.api.kaggle_api_extended import KaggleApi
import zipfile
import requests
# import requests_cache
import lastfmcreds
# requests_cache.install_cache()


# 1. Sheffield Gigs 
# Open the url
source = urllib.request.urlopen('https://www.sheffieldmusicscene.co.uk/w_city_by_date_Sheffield.html').read()
soup = bs.BeautifulSoup(source,'lxml')

# Read the webpage to a pandas df
table = soup.find_all('table')
gigs = pd.read_html(str(table))[0][['Date','Event Title','Venue']]
gigs = gigs.rename(columns={"Event Title": "artist"})
gigs['Date'] = gigs['Date'].str[:10]
gigs['artist'] = gigs['artist'].str.lower()


# 2. Last fm plays
def lastfm_get(payload):
    # define headers and URL
    headers = {'user-agent': lastfmcreds.USER_AGENT}
    url = 'https://ws.audioscrobbler.com/2.0/'

    # Add API key and format to the payload
    payload['api_key'] = lastfmcreds.API_KEY
    payload['format'] = 'json'
    payload['user'] = lastfmcreds.USER_AGENT

    response = requests.get(url, headers=headers, params=payload)
    return response

responses = []
page = 1
total_pages = 99999 # this is just a dummy number so the loop starts

while page <= total_pages:
    payload = {
        'method': 'user.gettopartists',
        'limit': 500,
        'page': page
    }

    # print some output so we can see the status
    print("Requesting last fm page {}/{}".format(page, total_pages))

    # make the API call
    response = lastfm_get(payload)

    # if we get an error, print the response and halt the loop
    if response.status_code != 200:
        print(response.text)
        break

    # extract pagination info
    page = int(response.json()['topartists']['@attr']['page'])
    total_pages = int(response.json()['topartists']['@attr']['totalPages'])

    # append response
    responses.append(response)

    # if it's not a cached result, sleep
    if not getattr(response, 'from_cache', False):
        time.sleep(0.25)

    # increment the page number
    page += 1
    
# Concat the data and move to dataframe
frames = [pd.DataFrame(r.json()['topartists']['artist']) for r in responses]
lastfm = pd.concat(frames)
lastfm = lastfm[['name','playcount']]
lastfm['playcount'] = lastfm['playcount'].astype(int)
lastfm = lastfm.rename(columns={"name": "artist", "playcount": "lastfm_playcount"})
lastfm['artist'] = lastfm['artist'].str.lower()


# Merge play count to the gigs
gigs = pd.merge(gigs, lastfm, on='artist', how='left')


# 3. Pitchfork Reviews
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


# 4. Theneedledrop Reviews
# Authenticate kaggle api 
api = KaggleApi()
api.authenticate()

# Download and upzip the kaggle file
api.dataset_download_files('borgesborges/theneedledrops-reviews', path='Documents/Data')
with zipfile.ZipFile('Documents/Data/theneedledrops-reviews.zip', 'r') as zipref:
    zipref.extractall('Documents/Data')

tnd = pd.read_json('Documents/Data/fantanodataset/theneedledrop.json')[['artist','title','score']]
tnd = tnd.rename(columns={"score": "TND-score","title":"album"})
tnd['artist'] = tnd['artist'].str.lower()
tnd['album'] = tnd['album'].str.lower()
tnd['mergekey'] = tnd['artist']+tnd['album']
tnd = tnd.sort_values(by=['mergekey'], ascending=False)
tnd = tnd.drop_duplicates()


# 5 Combine pitchfork, TND reviews and last fm plays
index = pitchfork.append(tnd)['mergekey'].sort_values().drop_duplicates()

reviews = pd.merge(index, pitchfork, on='mergekey', how='left')
reviews = pd.merge(reviews, tnd, on='mergekey', how='left')

reviews['artist'] = reviews.artist_x.combine_first(reviews.artist_y)
reviews['album'] = reviews.album_x.combine_first(reviews.album_y)
reviews = reviews[['artist','album','pitchfork-score','TND-score']]

# Merge the reviews to the gigs
df = pd.merge(gigs, reviews, on='artist', how='left')

df = df[df['lastfm_playcount'].notna() | df['pitchfork-score'].notna() | df['TND-score'].notna()]


