import argparse, re

argparser = argparse.ArgumentParser()

argparser.add_argument('playlist', help='Spotify Playlist')
argparser.add_argument('--offset', help='Offset at which to start')
argparser.add_argument('--out', help='File to which to write the results')
argparser.add_argument('--nofile', help='File to which to write the results')

args = argparser.parse_args()

try:
    __import__("credentials")
except ImportError:
    print("Please create a credentials.py file!")
    exit(1)

playlist_link = args.playlist
offset = int(args.offset) if args.offset is not None else 0

url_regex = re.compile("%s([a-zA-Z0-9]*)%s([a-zA-Z0-9]*)" % (re.escape("https://open.spotify.com/user/"), re.escape("/playlist/")))
url_regex_result = url_regex.search(playlist_link)

user_id = url_regex_result.group(1)
playlist_id = url_regex_result.group(2)

import spotify

spotify.analyze_playlist(user_id, playlist_id, offset, args.out, args.nofile)
