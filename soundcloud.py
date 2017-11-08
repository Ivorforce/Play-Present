import requests
import urllib
from lxml import html
from cssselect import GenericTranslator
import re

TRACK_VARIATION_MIN = 0.9
TRACK_VARIATION_MAX = 1.1  # .1 difference for production changes
TRACK_VARIATION_MS = 1000 * 30  # 30 Seconds in case some intro / outro was added

purchase_title_regex = re.compile(re.escape("\"purchase_title\":\"") + "([^\"]*)")
duration_regex = re.compile(re.escape("\"full_duration\":") + "([^,]*)")
direct_download_regex = re.compile("%s[0-9]*%s" % (re.escape("https://api.soundcloud.com/tracks/"), re.escape("/download")))


def free_purchase_title(song_html):
    purchase_title_result = purchase_title_regex.search(song_html)
    purchase_title = purchase_title_result.group(1).lower() if purchase_title_result else ""
    return "free download" in purchase_title or "free dl" in purchase_title


def free_song_title(song_tree):
    song_title = song_tree.findtext(".//title").lower()
    return "free download" in song_title or "free dl" in song_title


def free_download_included(song_html):
    return True if direct_download_regex.search(song_html) else False


def try_track(track, number, write_out=lambda x: None, track_out="%d %s @ %s"):
    query = ", ".join(track.artists) + " - " + track.title
    query_url = "https://soundcloud.com/search/sounds?q=" + urllib.parse.quote(query, safe='')
    search_request = requests.get(query_url)

    search_tree = html.fromstring(search_request.text)
    search_elements = search_tree.xpath(GenericTranslator().css_to_xpath('ul>li>h2>a'))

    if len(search_elements) == 0:
        return False

    href = search_elements[0].get('href')

    track_url = "https://soundcloud.com" + href
    song_html = requests.get(track_url).text

    duration_result = duration_regex.search(song_html)
    duration = int(duration_result.group(1).lower()) if duration_result else None

    if duration:
        if (duration < track.duration * TRACK_VARIATION_MIN - TRACK_VARIATION_MS
            or duration > track.duration * TRACK_VARIATION_MAX + TRACK_VARIATION_MS):
            return False

    if not free_purchase_title(song_html) or free_download_included(song_html) or free_song_title(
            html.fromstring(song_html)):
        return False

    track_info = track_out % (number, query, track_url)
    print(track_info)
    write_out(track_info + "\n")

    return True
