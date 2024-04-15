from dotenv import load_dotenv
import os
from flask import Flask, redirect, session, request, render_template, jsonify
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# loads all methods in the database file
from database import *

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

# This is what connects the front end to the backend
app = Flask(__name__)
app.secret_key = client_secret

# Initialize SpotifyOAuth object within the route
sp_oauth = SpotifyOAuth(
        client_id = os.getenv("CLIENT_ID"),
        client_secret = os.getenv("CLIENT_SECRET"),
        redirect_uri = 'http://localhost:5000/callback',
        scope = 'user-read-private user-top-read user-library-read',
        cache_path=None
    )

def htmlForLoginButton():
    auth_url = sp_oauth.get_authorize_url()
    htmlLoginButton = "<a href='" + auth_url + "'>Login to Spotify</a>"
    return htmlLoginButton

def getUser():
    sp = spotipy.Spotify(auth=session['spotify_token_info']['access_token'])
    user_profile = sp.current_user()
    return user_profile

def getManySongData(songs):
    names = []
    pics = []
    artists = []
    previews = []
    for song in songs:
        names.append(song['name'])
        previews.append(song['preview_url'])
        for artist in song['artists']:
            artists.append(artist['name'])
            break # this makes sure only the first artist is appended
        cover_art_url = song['album']['images'][0]['url'] if len(song['album']['images']) > 0 else None
        pics.append(cover_art_url)
    songData = zip(pics, names, artists, previews)
    return songData

# --- routes ---
@app.route('/')
def index():

    # Get user's profile information
    token_info = session.get('spotify_token_info')

    if not token_info or sp_oauth.is_token_expired(token_info):
        # return redirect('/callback')
        return htmlForLoginButton()
    
    sp = spotipy.Spotify(auth=session['spotify_token_info']['access_token'])

    # user variables
    user_profile = getUser()
    username = user_profile['display_name']
    pfp = user_profile['images'][0]['url'] if user_profile['images'] else ''
    id = user_profile['id']

    # adding the user to the database if they are not already in there
    addUser(id)

    topSongs = sp.current_user_top_tracks(limit=6)['items']
    songData = getManySongData(topSongs)

    return render_template('profile.html', username=username, pfp=pfp, id=id, songData=songData)

@app.route('/callback')
def callback():
    # Parse authorization response
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['spotify_token_info'] = token_info
    return redirect('/')

@app.route('/logout')
def logout():
    session['spotify_token_info'] = None
    session.clear()
    return render_template('logout.html')

@app.route('/feed')
def feed():
    sp = spotipy.Spotify(auth=session['spotify_token_info']['access_token'])
    top_tracks = sp.current_user_top_tracks(limit=5, time_range='medium_term')
    top_track_ids = [track['id'] for track in top_tracks['items']]

    recommendations = sp.recommendations(seed_tracks=top_track_ids, limit=10)['tracks']
    songData = getManySongData(recommendations)
    
    return render_template('feed.html', songData=songData)

@app.route('/create', methods=['GET', 'POST'])
def create():
    songs = []
    if request.method == 'POST':
        print("CREATE IF CHUNK IN /CREATE")
        # search_query = request.args.get('search_query')
        # search_query = request.form['search_query']
        search_query = request.json.get('search_query')

        sp = spotipy.Spotify(auth=session['spotify_token_info']['access_token'])
        results = sp.search(q = search_query, limit = 5, type = 'track')
        songData = getManySongData(results['tracks']['items'])
        
        # have to convert zip to array of arrays for the JS
        for pic, name, artist, preview in songData:       
            song = [None] * 4
            song[0] = pic
            song[1] = name
            song[2] = artist
            song[3] = preview
            songs.append(song)
        
        songs = jsonify(songs)

        return songs
    else:
        return render_template('create.html', songs=songs)

@app.route('/create_post')
def create_post():
    return render_template('create_post.html')

@app.route('/post', methods=['POST'])
def post():
    if request.method == 'POST':
        userId = getUser()['id']
        # selection will come from irene's search function
        songId = request.form['selection']
        description = request.form['description']

        data = (userId, songId, description)
        addPost(data)
        
        return 'Form submitted successfully!'

if __name__ == '__main__':
    app.run(port=5000, debug=True)
