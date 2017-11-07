import requests
import urllib
from lxml import html
from cssselect import GenericTranslator
import re

purchase_title_regex = re.compile(re.escape("\"purchase_title\":\"") + "([^\"]*)")
duration_regex = re.compile(re.escape("\"full_duration\":") + "([^,]*)")

def try_tracks(tracks, write_out=lambda x: None):
    searched = 0

    for track in tracks:
        query = ", ".join(track.artists) + " - " + track.title
        query_url = "https://soundcloud.com/search/sounds?q=" + urllib.parse.quote(query, safe='')
        request = requests.get(query_url)

        tree = html.fromstring(request.text)
        elements = tree.xpath(GenericTranslator().css_to_xpath('ul>li>h2>a'))

        if len(elements) == 0:
            continue

        href = elements[0].get('href')

        track_url = "https://soundcloud.com" + href
        song_html = requests.get(track_url).text

        song_title = html.fromstring(song_html).findtext(".//title").lower()

        purchase_title_result = purchase_title_regex.search(song_html)
        purchase_title = purchase_title_result.group(1).lower() if purchase_title_result else ""

        duration_result = duration_regex.search(song_html)
        duration = int(duration_result.group(1).lower()) if duration_result else None

        duration_similar = duration > track.duration * 0.7 and duration < track.duration * 1.3 if duration else True

        if duration_similar and \
                ("free download" in purchase_title or "free dl" in purchase_title
                or "free download" in song_title or "free dl" in song_title):
            track_info = "%s @ %s" % (query, track_url)
            print(track_info)
            write_out(track_info + "\n")

        searched += 1
        if searched % 20 == 0:
            print("Searched %d tracks" % searched)
