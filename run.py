import sys, argparse
import re

from credentials import app_id, app_secret, redirect_uri

from soundcloud import try_tracks

scope = 'user-library-read'

if len(sys.argv) > 2:
    username = sys.argv[1]
    playlist_link = sys.argv[2]
    offset = sys.argv[3] if len(sys.argv) > 3 else 0
else:
    print("Usage: %s username playlist_link" % (sys.argv[0],))
    sys.exit(1)

url_regex = re.compile("%s([0-9]*)%s([a-zA-Z0-9]*)" % (re.escape("https://open.spotify.com/user/"), re.escape("/playlist/")))
url_regex_result = url_regex.search(playlist_link)

user_id = url_regex_result.group(1)
playlist_id = url_regex_result.group(2)

import spotipy
import spotipy.util as util

token = util.prompt_for_user_token(username, scope, app_id, app_secret, redirect_uri)

if not token:
    print("Can't get token for", username)
    exit(1)

print("Hello, %s!" % username)

sp = spotipy.Spotify(auth=token)

while offset >= 0:
    results = sp.user_playlist_tracks(user_id, playlist_id, limit=100, offset=offset)

    found_tracks = []

    for item in results['items']:
        track = item['track']
        found_tracks.append(track['artists'][0]['name'] + " - " + track['name'])

    if len(found_tracks) == 0:
        print("Done!")
        exit(0)
    else:
        print("\nFound %d tracks between offset %d and %d - Crawling..." % (len(found_tracks), offset, offset + 100))
        try_tracks(found_tracks)
        offset += len(found_tracks)
