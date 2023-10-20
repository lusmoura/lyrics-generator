import os
from dotenv import load_dotenv
from flask import Flask, request, redirect, session, url_for, render_template
import requests
import cohere
import lyricsgenius as lg
from datetime import datetime

load_dotenv('.env')
app = Flask(__name__)
app.secret_key=os.environ["APP_SECRET_KEY"]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    auth_url = os.environ["SPOTIFY_AUTH_URL"] + '?response_type=code&client_id=' + os.environ["SPOTIFY_CLIENT_ID"] + '&redirect_uri=' + os.environ["SPOTIFY_REDIRECT_URI"] + '&scope=' + os.environ["SPOTIFY_SCOPES"]
    return redirect(auth_url)

@app.route('/logout')
def logout():
    if 'access_token' not in session:
        return redirect(url_for('login'))

    session.clear()
    return redirect(url_for('home'))

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_data = {
        'code': code,
        'redirect_uri': os.environ["SPOTIFY_REDIRECT_URI"],
        'client_id': os.environ["SPOTIFY_CLIENT_ID"],
        'client_secret': os.environ["SPOTIFY_CLIENT_SECRET"],
        'grant_type': 'authorization_code'
    }

    # Exchange the authorization code for an access token
    response = requests.post(os.environ["SPOTIFY_TOKEN_URL"], data=token_data)
    token_info = response.json()

    if 'access_token' not in token_info:
        return redirect(url_for('login'))

    # Store the access token in the session for future use
    session['access_token'] = token_info['access_token']

    return redirect(url_for('top'))

@app.route('/top')
def top():
    if 'access_token' not in session:
        return redirect(url_for('login'))
    
    ACCESS_TOKEN = session['access_token']

    # Define your desired parameters
    params = {
        'limit': 5,  # Adjust the number of top tracks you want to retrieve
        'time_range': 'short_term'  # You can change 'time_range' to 'medium_term' or 'long_term'
    }

    # Set the Authorization header with the bearer token
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}'
    }

    # Make the API request
    response = requests.get(os.environ["SPOTIFY_API_URL"], params=params, headers=headers)

    # return a list of the user's top tracks and a button to generate lyrics
    if response.status_code != 200:
        return render_template('error.html', status_code=response.status_code)

    # top_tracks = response.json()
    top_tracks = response.json()
    
    # create list of song names and artists with list comprehension
    track_list = []
    for track in top_tracks['items']:
        song_name = track["name"]
        artits = [artist['name'] for artist in track['artists']]
        track_list.append({"name": song_name, "artists": artits})

    # store top tracks in session
    session['songs'] = track_list

    return render_template('top.html', top_tracks=track_list, last_updated=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

@app.route('/generate')
def generate():
    if 'access_token' not in session:
        return redirect(url_for('login'))
    
    # get top tracks from session
    songs = session['songs']

    # create prompt
    if 'prompt' not in session:
        build_prompt(songs)

    prompt = session['prompt']

    # generate new lyrics
    co = cohere.Client(os.environ['COHERE_API_KEY'])
    res = co.generate(prompt=prompt, temperature=1.5, frequency_penalty=0.8, presence_penalty=1)
    lyrics = res.generations[0].text.strip().replace('--', '').strip()

    return render_template('generate.html', top_tracks=songs, generated_lyrics=lyrics)

def build_prompt(songs):
    prompt = '# TASK\nGiven the following lyrics separated by -- write one completely new song that represent the same style. Be creative and give JUST THE LYRICS.\n\n# EXISTING LYRICS\n'

    genius = lg.Genius(os.environ["GENIUS_API_KEY"])

    # add lyrics to prompt
    for song in songs:
        song = genius.search_song(song["name"], ','.join(song["artists"]))

        # clean lyrics, remove the first line
        lyrics = song.lyrics.split('\n')[1:]
        lyrics = '\n'.join(lyrics)

        # add the last word of the first line to the begginning of the lyrics
        first_line = song.lyrics.split('\n')[0]
        first_line = first_line.split('[')[-1]
        lyrics = '[' + first_line + '\n' + lyrics   

        # if the lytics end with Embed, remove the word Embed
        if lyrics.endswith('Embed'):
            lyrics = lyrics[:-6]

        prompt += lyrics
        prompt += '\n\n' + '-' * 2 + '\n\n'

    prompt += '# NEW LYRICS\n'
    session['prompt'] = prompt
    return prompt

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', status_code=404)

if __name__ == '__main__':
    app.run(debug=True, port=8888)
