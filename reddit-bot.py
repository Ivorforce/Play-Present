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

done_submissions = []
done_mentions = []

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

while True:
    try:
        for sub in relevant_subreddits:
            subreddit = r.subreddit(sub)

            for submission in subreddit.hot(limit=10):
                if submission.id not in done_submissions:
                    done_submissions.append(submission.id)

                    tracks = free_tracks_from_body(submission.selftext.lower(), submission.url)

                    if (len(tracks) > 0):
                        submission.reply(reply_text(tracks))
                        print("Replied to submission " + submission.id)

        for comment in r.inbox.mentions(limit=10):
            if comment.id not in done_mentions:
                done_mentions.append(comment.id)

                tracks = free_tracks_from_body(comment.body)

                comment.reply(reply_text(tracks))
                print("Replied to comment " + comment.id)

        time.sleep(60 * 10)
    except praw.exceptions.APIException as ex:
        print(ex) # But try again
        time.sleep(60 * 10) # Later

