import requests
import urllib
from lxml import html
from cssselect import GenericTranslator

def try_tracks(tracks):
    searched = 0

    for track in tracks:
        query = "https://soundcloud.com/search?q=" + urllib.parse.quote(track, safe='')
        tree = html.fromstring(requests.get(query).text)

        elements = tree.xpath(GenericTranslator().css_to_xpath('ul>li>h2>a'))

        if len(elements) == 0:
            continue

        href = elements[0].get('href')

        track_url = "https://soundcloud.com" + href
        song_html = requests.get(track_url).text
        if ("Free Download" in song_html):
            print("%s (%s)" % (track, track_url))

        searched += 1
        if searched % 20 == 0:
            print("Searched %d tracks" % searched)

