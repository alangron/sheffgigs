

import pandas as pd

# 2. Pitchfork Reviews
# Taken from here https://www.lamorbidamacchina.com/pitchforkscores/export.php
pitchfork = pd.read_csv('C:/Users/Administrator/Documents/GitHub/sheffgigs/Data/pitchfork-scores-export.csv',sep=';')[['score','author','title']]
pitchfork = pitchfork.rename(columns={"author": "artist", "title": "album"})

df_hist = pd.read_csv('C:/Users/Administrator/Documents/GitHub/sheffgigs/Data/pitchfork.csv')[['artist','album','score']]

pitchfork = pitchfork.append(df_hist)

pitchfork = pitchfork.rename(columns={"score": "pitchfork-score"})

pitchfork['artist'] = pitchfork['artist'].str.lower()
pitchfork['album'] = pitchfork['album'].str.lower()
pitchfork['mergekey'] = pitchfork['artist']+pitchfork['album']
pitchfork = pitchfork.sort_values(by=['mergekey'], ascending=False)
pitchfork = pitchfork.drop_duplicates()


# 3. Theneedledrop Reviews
# TND Data from https://www.kaggle.com/datasets/josephgreen/anthony-fantano-album-review-dataset/code?select=albums.csv
tnd = pd.read_csv('C:/Users/Administrator/Documents/GitHub/sheffgigs/Data/albums.csv')[['project_name','artist','rating']]
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
reviews = reviews[['artist','album','mergekey','pitchfork-score','TND-score']]
