import pandas as pd
import urllib.request
import bs4 as bs

# 1. Sheffield Gigs
# Open the url
source = urllib.request.urlopen('https://www.sheffieldmusicscene.co.uk/w_city_by_date_Sheffield.html').read()
soup = bs.BeautifulSoup(source,'lxml')

# Read the webpage to a pandas df
table = soup.find_all('table')
gigs = pd.read_html(str(table))[0][['Date','Event Title','Venue']]
gigs = gigs.rename(columns={"Event Title": "artist"})
gigs['Date'] = gigs['Date'].str[:10]

# 2. Pitchfork Reviews
# Taken from here https://www.lamorbidamacchina.com/pitchforkscores/export.php
reviews = pd.read_csv('C:/Users/Administrator/Documents/GitHub/sheffgigs/Data/pitchfork-scores-export.csv',sep=';')[['score','author','title']]
reviews = reviews.rename(columns={"author": "artist", "title": "album"})

df_hist = pd.read_csv('C:/Users/Administrator/Documents/GitHub/sheffgigs/Data/pitchfork.csv')[['artist','album','score']]

reviews = reviews.append(df_hist)
reviews = reviews.drop_duplicates()

# Merge the reviews to the gigs
df = pd.merge(gigs, reviews, on='artist', how='inner')
df = df.sort_values(by=['score'], ascending=False)
