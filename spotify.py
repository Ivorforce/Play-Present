import credentials

import spotipy, re
import spotipy.util as util

scope = 'user-library-read'

playlist_regex = re.compile("%s([a-zA-Z0-9]*)%s([a-zA-Z0-9]*)" % (re.escape("https://open.spotify.com/user/"), re.escape("/playlist/")))


def get_token():
    token = util.prompt_for_user_token(credentials.spotify_username, scope, credentials.app_id, credentials.app_secret,
                                       credentials.redirect_uri)

    if not token:
        print("Can't get token for '%s'" % credentials.spotify_username)
        exit(1)
    else:
        return token


def get_spotify():
    return spotipy.Spotify(auth=get_token())


def playlist_name(user_id, playlist_id):
    return get_spotify().user_playlist(user_id, playlist_id)['name']


def create_track(title, artists, duration):
    track = lambda: None
    setattr(track, 'title', title)
    setattr(track, 'artists', artists)
    setattr(track, 'duration', duration)
    return track


def analyze_playlist(callback, user_id, playlist_id, offset=0, limit=100000, result_limit=1000):
    while True:
        result_section = get_spotify().user_playlist_tracks(user_id, playlist_id, limit=100, offset=offset)
        result_section_tracks = result_section['items']

        if len(result_section_tracks) == 0:
            return True

        for item in result_section_tracks:
            spotify_track = item['track']

            if spotify_track:  # Apparently this can happen
                track = create_track(spotify_track['name'],
                                     map(lambda artist: artist['name'], spotify_track['artists']),
                                     spotify_track['duration_ms'])

                if callback(track, offset):
                    result_limit -= 1
                    if result_limit < 0:
                        return False

            offset += 1
            if offset >= limit:
                return False

        if (len(result_section_tracks) < 100):  # Don't need the last request, we're already done
            return True
