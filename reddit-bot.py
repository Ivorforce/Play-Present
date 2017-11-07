import time
import re, os
import praw

import spotify
import soundcloud

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

    global track_num
    track_num = 0

    def try_tracks(tracks):
        global track_num

        for track in tracks:
            track_num += 1
            soundcloud.try_track(track, track_num, lambda s: found_tracks.append(s), "%d %s @ [Soundcloud](%s)")

    if not spotify.analyze_playlist(try_tracks, user_id, playlist_id, 0):
        found_tracks.append("... stopped due to timeout! Try a smaller playlist :)\n")

    return found_tracks

def free_tracks_from_body(body, url=""):
    url_regex_result = url_regex.search(url) or url_regex.search(body)
    if url_regex_result:
        return free_tracks(url_regex_result.group(1), url_regex_result.group(2))
    return []

def reply_text(tracks):
    if (len(tracks) > 0):
        track_list = "\n".join(tracks)
        return ("I found %d free %s in this playlist: \n\n%s%s" %
                     (len(tracks), ("track" if len(tracks) == 1 else "tracks"), track_list, bot_footer))
    else:
        return "I found no free tracks in this playlist :(%s" % bot_footer

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

while True:
    try:
        for sub in relevant_subreddits:
            subreddit = r.subreddit(sub)

            for submission in subreddit.hot(limit=10):
                if submission.id not in done_submissions:
                    print("Searching playlist for submission " + submission.id)
                    tracks = free_tracks_from_body(submission.selftext.lower(), submission.url)

                    if (len(tracks) > 0) or sub not in quiet_subreddits:
                        submission.reply(reply_text(tracks))
                        print("Replied to submission " + submission.id)

                    done_submissions.append(submission.id)

        for comment in r.inbox.mentions(limit=10):
            if comment.id not in done_mentions:
                print("Searching playlist for comment " + comment.id)
                tracks = free_tracks_from_body(comment.body)

                comment.reply(reply_text(tracks))
                print("Replied to comment " + comment.id)

                done_mentions.append(comment.id)

        with open(submission_store, "w") as store:
            print(done_submissions)
            store.write("\n".join(done_submissions))
        with open(mention_store, "w") as store:
            store.write("\n".join(done_mentions))

        time.sleep(60 * 10)

    except praw.exceptions.APIException as ex:
        print(ex) # But try again
        time.sleep(60 * 10) # Later

