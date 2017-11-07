# Play//Present
A dumb tool for new DJs to find free releases in their Spotify playlists.

To run, add a credentials.py file like this:

    spotify_username = "some_username" # Your Spotify Username

    app_id="some_app_id" # This Spotify app's ID
    app_secret="some_app_secret" # This Spotify app's Secret
    redirect_uri="some_redirect_uri" # This Spotify app's redirect uri
    
as per the [Spotify API](https://developer.spotify.com/my-applications/#!/applications).

Then, run

    python run.py playlist_link
    
which will crawl your playlist's tracks and write it to a file.

To continue a previous search, include the --offset parameter:

    python run.py playlist_link --offset 1000
