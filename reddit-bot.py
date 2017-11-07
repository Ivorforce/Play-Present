import time
import re
import praw

import spotify
import soundcloud

bot_footer = """

---

^I&#32;am&#32;a&#32;bot.&#32;|&#32;[Source](https://github.com/Ivorforce/Play-Present)&#32;|&#32;[Author](https://www.reddit.com/user/Ivorius/)
"""

relevant_subreddits = ["playpresent"]

r = praw.Reddit('play-present-bot', user_agent='play-present-bot user agent')

####

already_done = []

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

    spotify.analyze_playlist(try_tracks, user_id, playlist_id, 0)

    return found_tracks

while True:
    try:
        for sub in relevant_subreddits:
            subreddit = r.subreddit(sub)

            for submission in subreddit.hot(limit=10):
                in_link = submission.url
                op_text = submission.selftext.lower()

                url_regex_result = url_regex.search(in_link) or url_regex.search(op_text)

                if submission.id not in already_done and url_regex_result:
                    already_done.append(submission.id)

                    tracks = free_tracks(url_regex_result.group(1), url_regex_result.group(2))

                    if (len(tracks) > 0):
                        track_list = "\n".join(tracks)
                        submission.reply("I found %d free %s in this playlist: \n\n%s%s" %
                                         (len(tracks), ("track" if len(tracks) == 1 else "tracks"), track_list, bot_footer))
                        print("Replied to " + submission.id)

            time.sleep(60 * 10)
    except praw.exceptions.APIException as ex:
        print(ex) # But try again
        time.sleep(60 * 10) # Later

