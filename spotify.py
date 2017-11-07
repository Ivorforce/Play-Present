import os
import re

import credentials

import spotipy
import spotipy.util as util
import soundcloud

scope = 'user-library-read'

def analyze_playlist(user_id, playlist_id, offset, out = lambda: None, nofile = False):

    token = util.prompt_for_user_token(credentials.spotify_username, scope, credentials.app_id, credentials.app_secret, credentials.redirect_uri)

    if not token:
        print("Can't get token for '%s'" % credentials.spotify_username)
        exit(1)

    print("Hello, %s!" % credentials.spotify_username)

    sp = spotipy.Spotify(auth=token)

    playlist = sp.user_playlist(user_id, playlist_id)
    print("Searching playlist: %s" % playlist['name'])

    if not out and not nofile:
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

            soundcloud.try_tracks(found_tracks, write_out=write_out)
            offset += len(found_tracks)
