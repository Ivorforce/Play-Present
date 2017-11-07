# Play//Present
A dumb tool for new DJs to find free releases in their Spotify playlists.

## Try

You can most easily use me by posting a playlist link to [/r/playpresent](https://www.reddit.com/r/playpresent/)

## Install

Install dependencies:

    pip3 install spotipy soundcloud cssselect lxml
    pip install praw # For the Reddit Bot

Add a credentials.py file like this:

    spotify_username = "some_username" # Your Spotify Username

    app_id="some_app_id" # This Spotify app's ID
    app_secret="some_app_secret" # This Spotify app's Secret
    redirect_uri="some_redirect_uri" # This Spotify app's redirect uri

(As per the [Spotify API](https://developer.spotify.com/my-applications/#!/applications))

If you want to run the reddit bot, you also need to provide a praw.ini file.

## Run

Run

    python run.py playlist_link
    
which will crawl your playlist's tracks and write it to a file.

To continue a previous search, include the --offset parameter:

    python run.py playlist_link --offset 1000

To run the bot, run

    python reddit-bot.py
    
## Support

While you're here, why not check me out on soundcloud: [Lukas Tenbrink on Soundcloud](http://soundcloud.com/lukastenbrink)
