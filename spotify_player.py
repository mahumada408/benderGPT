import spotipy
from spotipy.oauth2 import SpotifyOAuth

def play_spotify_song(search_query):
    scope = 'user-modify-playback-state user-read-playback-state'

    # Authenticate with Spotify using Spotipy
    sp = spotipy.Spotify(client_credentials_manager=SpotifyOAuth(scope=scope))

    # Input search query from the user
    # search_query = "artist, Rush, song, Subdivisions"

    # Perform search on Spotify
    result = sp.search(q=search_query, limit=1, type='track')
    tracks = result['tracks']['items']
    
    if tracks:
        # Get the first track's URI
        track_uri = tracks[0]['uri']
        track_name = tracks[0]['name']
        artist_name = tracks[0]['artists'][0]['name']
        
        # Play the track on the active device
        try:
            sp.start_playback(uris=[track_uri])
            print(f"Playing '{track_name}' by {artist_name}")
            return True
        except spotipy.SpotifyException as e:
            print(f"An error occurred: {e}")
    else:
        print("No results found for your query.")
        return False

def stop_spotify():
    scope = 'user-modify-playback-state user-read-playback-state'

    # Authenticate with Spotify using Spotipy
    sp = spotipy.Spotify(client_credentials_manager=SpotifyOAuth(scope=scope))

    # Attempt to pause playback
    try:
        sp.pause_playback()
        print("Spotify playback has been stopped.")
        return False
    except spotipy.SpotifyException as e:
        print(f"An error occurred: {e}")
        return True

if __name__ == '__main__':
    main()
