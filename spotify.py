import credentials

import spotipy
import spotipy.util as util

scope = 'user-library-read'

token = util.prompt_for_user_token(credentials.spotify_username, scope, credentials.app_id, credentials.app_secret,
                                   credentials.redirect_uri)

if not token:
    print("Can't get token for '%s'" % credentials.spotify_username)
    exit(1)

sp = spotipy.Spotify(auth=token)

def playlist_name(user_id, playlist_id):
    return sp.user_playlist(user_id, playlist_id)['name']

def analyze_playlist(callback, user_id, playlist_id, offset):

    token = util.prompt_for_user_token(credentials.spotify_username, scope, credentials.app_id, credentials.app_secret, credentials.redirect_uri)

    if not token:
        print("Can't get token for '%s'" % credentials.spotify_username)
        exit(1)

    sp = spotipy.Spotify(auth=token)

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
            return
        else:
            callback(found_tracks)
            offset += len(found_tracks)
