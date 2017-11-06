# Spotifree
A dumb tool for new DJs to find free tracks from their Spotify playlists.

To run, add a credentials.py file like this:

    app_id=""
    app_secret=""
    redirect_uri=""
    
as per the Spotify API.

Then, run

    python run.py username user_id playlist_id
    
which will crawl your playlist's tracks.
