
# API details can be found here https://www.last.fm/api/account/
# Tutorial https://www.dataquest.io/blog/last-fm-api-python/
import requests
import time
import requests_cache
import pandas as pd
import lastfmcreds
requests_cache.install_cache()

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
    print("Requesting page {}/{}".format(page, total_pages))

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
lastfm = lastfm.rename(columns={"name": "artist", "playcount": "lastfm_playcount"})
lastfm['artist'] = lastfm['artist'].str.lower()



