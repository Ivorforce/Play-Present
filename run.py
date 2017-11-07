import os, sys, argparse
import re

from credentials import app_id, app_secret, redirect_uri, spotify_username

from soundcloud import try_tracks

scope = 'user-library-read'

argparser = argparse.ArgumentParser()

argparser.add_argument('playlist', help='Spotify Playlist')
argparser.add_argument('--offset', help='Offset at which to start')
argparser.add_argument('--out', help='File to which to write the results')
argparser.add_argument('--nofile', help='File to which to write the results')

args = argparser.parse_args()

playlist_link = args.playlist
offset = int(args.offset) if args.offset is not None else 0
out = args.out

url_regex = re.compile("%s([a-zA-Z0-9]*)%s([a-zA-Z0-9]*)" % (re.escape("https://open.spotify.com/user/"), re.escape("/playlist/")))
url_regex_result = url_regex.search(playlist_link)

user_id = url_regex_result.group(1)
playlist_id = url_regex_result.group(2)

import spotipy
import spotipy.util as util

token = util.prompt_for_user_token(spotify_username, scope, app_id, app_secret, redirect_uri)

if not token:
    print("Can't get token for '%s'" % spotify_username)
    exit(1)

print("Hello, %s!" % spotify_username)

sp = spotipy.Spotify(auth=token)

playlist = sp.user_playlist(user_id, playlist_id)
print("Searching playlist: %s" % playlist['name'])

if not out and not args.nofile:
    if not os.path.exists("results"):
        os.makedirs("results")
    out = os.path.abspath("results/%s.txt") % re.sub(r'\W+', '', playlist['name'])

if out:
    print("Writing to: %s" % out)
def write_out(string):
    if out:
        with open(out, "a") as myfile:
            myfile.write(string)

while offset >= 0:
    results = sp.user_playlist_tracks(user_id, playlist_id, limit=100, offset=offset)

    found_tracks = []

    for item in results['items']:
        spotify_track = item['track']
        track = lambda: None
        setattr(track, 'title', spotify_track['name'])
        setattr(track, 'artists', map(lambda artist: artist['name'], spotify_track['artists']))
        setattr(track, 'duration', spotify_track['duration_ms'])
        found_tracks.append(track)

    if len(found_tracks) == 0:
        print("Done!")
        write_out("Done!")
        exit(0)
    else:
        print("\nFound %d tracks between offset %d and %d - Crawling..." % (len(found_tracks), offset, offset + 100))
        write_out("At offset %d\n" % offset)

        try_tracks(found_tracks, write_out=write_out)
        offset += len(found_tracks)
