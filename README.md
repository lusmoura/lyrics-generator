# lyrics-generator
Connect to your Spotify account and generate a brand new song based to your top tracks

## How does it work
Log in with your Spotify account so that we can access your top tracks. We will then use the lyrics of your top tracks to generate a brand new song.


## How to run
1. Clone the repository
2. Install the dependencies with `pip install -r requirements.txt`
3. Create a Spotify dev account and register your app [here](https://developer.spotify.com/dashboard/applications)
   1. Notice that you will need to set the redirect URI to the same value as the `SPOTIFY_REDIRECT_URI` environment variable
4. Create a Genius dev account and register your app [here](https://genius.com/api-clients)
5. Create a `.env` file with the following content:
```
SPOTIFY_CLIENT_ID
SPOTIFY_CLIENT_SECRET
SPOTIFY_REDIRECT_URI
SPOTIFY_API_BASE
SPOTIFY_SCOPES
SPOTIFY_AUTH_URL
SPOTIFY_TOKEN_URL
SPOTIFY_API_URL
GENIUS_API_KEY
COHERE_API_KEY
APP_SECRET_KEY
```

6. Run the app with `python app.py`
7. Open your browser and go to `http://localhost:8888/`
8. Log in with your Spotify account
9. Enjoy your brand new song!