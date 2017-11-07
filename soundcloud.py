import requests
import urllib
from lxml import html
from cssselect import GenericTranslator
import re

TRACK_VARIATION_MIN = 0.9
TRACK_VARIATION_MAX = 1.1 # .1 difference for production changes
TRACK_VARIATION_MS = 1000 * 30 # 30 Seconds in case some intro / outro was added

purchase_title_regex = re.compile(re.escape("\"purchase_title\":\"") + "([^\"]*)")
duration_regex = re.compile(re.escape("\"full_duration\":") + "([^,]*)")

def try_track(track, number, write_out = lambda x: None, track_out = "%d %s @ %s"):
    query = ", ".join(track.artists) + " - " + track.title
    query_url = "https://soundcloud.com/search/sounds?q=" + urllib.parse.quote(query, safe='')
    request = requests.get(query_url)

    tree = html.fromstring(request.text)
    elements = tree.xpath(GenericTranslator().css_to_xpath('ul>li>h2>a'))

    if len(elements) == 0:
        return

    href = elements[0].get('href')

    track_url = "https://soundcloud.com" + href
    song_html = requests.get(track_url).text

    song_title = html.fromstring(song_html).findtext(".//title").lower()

    purchase_title_result = purchase_title_regex.search(song_html)
    purchase_title = purchase_title_result.group(1).lower() if purchase_title_result else ""

    duration_result = duration_regex.search(song_html)
    duration = int(duration_result.group(1).lower()) if duration_result else None

    duration_similar = duration > track.duration * TRACK_VARIATION_MIN - TRACK_VARIATION_MS \
                       and duration < track.duration * TRACK_VARIATION_MAX + TRACK_VARIATION_MS \
        if duration else True

    is_free_track = duration_similar and \
            ("free download" in purchase_title or "free dl" in purchase_title
             or "free download" in song_title or "free dl" in song_title)

    if not is_free_track:
        return False

    track_info = track_out % (number, query, track_url)
    print(track_info)
    write_out(track_info + "\n")

    return True
