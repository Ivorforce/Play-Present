import requests
import urllib
from lxml import html
from cssselect import GenericTranslator
import re

purchase_title_regex = re.compile(re.escape("\"purchase_title\":\"") + "([^\"]*)")

def try_tracks(tracks, write_out=lambda x: None):
    searched = 0

    for track in tracks:
        query = "https://soundcloud.com/search/sounds?q=" + urllib.parse.quote(track, safe='')
        request = requests.get(query)

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

        if "free download" in purchase_title or "free dl" in purchase_title\
                or "free download" in song_title or "free dl" in song_title:
            track_info = "%s (%s)" % (track, track_url)
            print(track_info)
            write_out(track_info + "\n")

        searched += 1
        if searched % 20 == 0:
            print("Searched %d tracks" % searched)
