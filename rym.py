# Code snippets from https://github.com/dbeley/rymscraper

import pandas as pd
import os
from rymscraper import rymscraper, RymUrl
import urllib.request
import bs4 as bs
network = rymscraper.RymNetwork()

# 1. Sheffield Gigs
# Open the url
source = urllib.request.urlopen('https://www.sheffieldmusicscene.co.uk/w_city_by_date_Sheffield.html').read()
soup = bs.BeautifulSoup(source,'lxml')

# Read the webpage to a pandas df
table = soup.find_all('table')
gigs = pd.read_html(str(table))[0][['Date','Event Title','Venue']]
gigs = gigs.rename(columns={"Event Title": "artist"})
gigs['Date'] = gigs['Date'].str[:10]



artist = gigs.loc[1,'artist']
discography_infos = network.get_discography_infos(name=artist, complementary_infos=False)
df = pd.DataFrame.from_records(discography_infos)
df = df[df['Category']=='Album'][['Artist','Name','Average Rating']]
df = df.rename(columns={"Name": "album", "Artist": "artist", "Average Rating": "Average RYM Rating"})

# Kill any firefox or geckdrivers left running
os.system("taskkill /im firefox.exe /f")
os.system("taskkill /im geckodriver.exe /f")
