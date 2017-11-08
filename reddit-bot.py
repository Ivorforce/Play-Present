import time
import re, os
import praw

import spotify
import soundcloud

import urllib3

bot_footer = """

---

^I&#32;am&#32;a&#32;bot.&#32;|&#32;[Source](https://github.com/Ivorforce/Play-Present)&#32;|&#32;[Author](https://www.reddit.com/user/Ivorius/)
"""

relevant_subreddits = ["playpresent"]
quiet_subreddits = []

r = praw.Reddit('play-present-bot', user_agent='play-present-bot user agent')

url_regex = re.compile("%s([a-zA-Z0-9]*)%s([a-zA-Z0-9]*)" % (re.escape("https://open.spotify.com/user/"), re.escape("/playlist/")))


def free_tracks(user_id, playlist_id):
    found_tracks = []

    def try_track(track, offset):
        return soundcloud.try_track(track, offset + 1, lambda s: found_tracks.append(s), "%d %s @ [Soundcloud](%s)")

    if not spotify.analyze_playlist(try_track, user_id, playlist_id, 0, limit = 5000, result_limit = 50):
        found_tracks.append("... stopped due to timeout! Try a smaller playlist :)\n")

    return found_tracks

def free_tracks_from_body(body, url=""):
    url_regex_result = url_regex.search(url) or url_regex.search(body)
    if url_regex_result:
        return free_tracks(url_regex_result.group(1), url_regex_result.group(2))
    return []

def reply_text(tracks, start_time):
    time_diff = time.time() - start_time
    time_comment = "This took me %d seconds!" % time_diff if time_diff < 120 else "This took me about %d minutes!" % int(time_diff / 60)

    if (len(tracks) > 0):
        track_list = "\n".join(tracks)
        if (len(track_list) > 9000): # Reddit Limit at 10 000
            track_list = track_list[:9000] + "...\n\n(This was cut because the post was too long!)"

        return ("I found %d free %s in this playlist: \n\n%s\n\n%s%s" %
                     (len(tracks), ("track" if len(tracks) == 1 else "tracks"), track_list, time_comment, bot_footer))
    else:
        return "I found no free tracks in this playlist :(\n\n%s%s" % (time_comment, bot_footer)

# Load

if not os.path.exists("store"):
    os.makedirs("store")

submission_store = "store/submissions"
try:
    with open(submission_store, "r") as store:
        done_submissions = store.read().split("\n")
except FileNotFoundError:
    done_submissions = []

mention_store = "store/mentions"
try:
    with open(mention_store, "r") as store:
        done_mentions = store.read().split("\n")
except FileNotFoundError:
    done_mentions = []

print("Hello, %s!" % spotify.credentials.spotify_username)
print("Checking posts...")

while True:
    try:
        cycle_start_time = time.time()

        for sub in relevant_subreddits:
            subreddit = r.subreddit(sub)

            for submission in subreddit.hot(limit=10):
                if submission.id not in done_submissions:
                    print("Searching playlist for submission " + submission.id)

                    start_time = time.time()
                    tracks = free_tracks_from_body(submission.selftext.lower(), submission.url)

                    if (len(tracks) > 0) or sub not in quiet_subreddits:
                        submission.reply(reply_text(tracks, start_time))
                        print("Replied to submission " + submission.id)

                    done_submissions.append(submission.id)
                    with open(submission_store, "a") as store:
                        store.write("\n" + submission.id)

        for comment in r.inbox.mentions(limit=10):
            if comment.id not in done_mentions:
                print("Searching playlist for comment " + comment.id)

                start_time = time.time()
                tracks = free_tracks_from_body(comment.body)

                comment.reply(reply_text(tracks, start_time))
                print("Replied to comment " + comment.id)

                done_mentions.append(comment.id)
                with open(mention_store, "a") as store:
                    store.write("\n" + comment.id)

        passed_time = (time.time() - cycle_start_time)
        time.sleep(max(60 * 10 - passed_time, 0)) # Take at most 60 * 10 seconds

    except praw.exceptions.APIException or urllib3.exceptions.MaxRetryError as ex:
        print(ex) # But try again
        time.sleep(60 * 10) # Later

