# Code snippets from https://github.com/dbeley/rymscraper

import pandas as pd
from rymscraper import rymscraper, RymUrl
import urllib.request
import bs4 as bs
import os
import time
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

artist = gigs.loc[0,'artist']
discography_infos = network.get_discography_infos(name=artist, complementary_infos=False)
rym = pd.DataFrame.from_records(discography_infos)
rym = rym[(rym['Ratings']!='')]
rym = rym[(rym['Category']=='Album') & (rym['Ratings'].astype(int)>=10)][['Artist','Name','Average Rating']]
rym = rym.rename(columns={"Name": "album", "Artist": "artist", "Average Rating": "Average RYM Rating"})
    
for x in range(1,len(gigs)):
    network = rymscraper.RymNetwork()
    try:
        artist = gigs.loc[x,'artist']
        print(artist)
        discography_infos = network.get_discography_infos(name=artist, complementary_infos=False)
        df = pd.DataFrame.from_records(discography_infos)
        df = df[(df['Ratings']!='')]
        df = df[(df['Category']=='Album') & (df['Ratings'].astype(int)>=10)][['Artist','Name','Average Rating']]
        df = df.rename(columns={"Name": "album", "Artist": "artist", "Average Rating": "Average RYM Rating"})
        rym = rym.append(df)
        rym.to_csv('C:/Users/Administrator/Documents/GitHub/sheffgigs/Data/rym.csv')
        # Kill any firefox or geckdrivers left running
        os.system("taskkill /im firefox.exe /f")
        os.system("taskkill /im geckodriver.exe /f")
        network.browser.close()
        network.browser.quit()
        time.sleep(30) #sleep to avoid rym blocking your IP address
    except:
        pass