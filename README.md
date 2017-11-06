# Spotifree
A dumb tool for new DJs to find free tracks from their Spotify playlists.

To run, add a credentials.py file like this:

    app_id=""
    app_secret=""
    redirect_uri=""
    
as per the Spotify API.

Then, run

    python run.py username playlist_link --out songs.txt
    
which will crawl your playlist's tracks.

To continue a previous search, include the --offset parameter:

    python run.py username playlist_link --out songs.txt --offset 1000
