# Play//Present
A dumb tool for new DJs to find free releases in their Spotify playlists.

To run, add a credentials.py file like this:

    spotify_username = 'some_username'
    app_id="some_app_id"
    app_secret="some_app_secret"
    redirect_uri="some_redirect_uri"
    
as per the [Spotify API](https://developer.spotify.com/my-applications/#!/applications).

Then, run

    python run.py playlist_link
    
which will crawl your playlist's tracks and write it to a file.

To continue a previous search, include the --offset parameter:

    python run.py playlist_link --offset 1000
