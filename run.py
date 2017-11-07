import argparse, re, os

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
import soundcloud

playlist_name = spotify.playlist_name(user_id, playlist_id)

print("Hello, %s!" % spotify.credentials.spotify_username)

out = args.out
if not out and not args.nofile:
    if not os.path.exists("results"):
        os.makedirs("results")
    out = os.path.abspath("results/%s.txt") % re.sub(r'\W+', '', playlist_name)

if out:
    print("Writing to: %s" % out)

def write_out(string):
    if out:
        with open(out, "a") as myfile:
            myfile.write(string)

print()

def try_track(track, offset):
    result = soundcloud.try_track(track, offset + 1, write_out)

    if offset % 20 == 0:
        print("Searched %d tracks" % offset)

    return result

print("Searching playlist: %s" % playlist_name)
write_out("From Playlist: %s\n" % playlist_name)
spotify.analyze_playlist(try_track, user_id, playlist_id, offset)

write_out("Done!\n")
