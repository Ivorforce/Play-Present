import spotipy
import spotipy.util as util
import sys

from credentials import app_id, app_secret, redirect_uri


scope = 'user-library-read'

if len(sys.argv) > 3:
    username = sys.argv[1]
    user_id = sys.argv[2]
    playlist_id = sys.argv[3]
else:
    print("Usage: %s username user_id playlist_id" % (sys.argv[0],))
    sys.exit(1)

token = util.prompt_for_user_token(username, scope, app_id, app_secret, redirect_uri)

if not token:
    print("Can't get token for", username)
    exit(1)

sp = spotipy.Spotify(auth=token)
results = sp.user_playlist_tracks(user_id, playlist_id)

try_tracks = []

for item in results['items']:
    track = item['track']
    try_tracks.append(track['name'] + " " + track['artists'][0]['name'])

print("Found %d tracks - Crawling..." % len(try_tracks))

import requests
import urllib
from lxml import html
from cssselect import GenericTranslator

skipped = 0

for track in try_tracks:
    query = "https://soundcloud.com/search?q=" + urllib.parse.quote(track, safe='')
    tree = html.fromstring(requests.get(query).text)

    elements = tree.xpath(GenericTranslator().css_to_xpath('ul>li>h2>a'))

    if len(elements) == 0:
        continue

    href = elements[0].get('href')

    track_url = "https://soundcloud.com" + href
    song_html = requests.get(track_url).text
    if ("Free Download" in song_html):
        if skipped > 0:
            print("Skipped %d tracks" % skipped)
        print("%s (%s)" % (track, track_url))
    else:
        skipped += 1

        if skipped >= 50:
            print("Skipped %d tracks" % skipped)
            skipped = 0

