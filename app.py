from dotenv import load_dotenv
import os
from flask import Flask, redirect, session, request, render_template, make_response
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

    topSongs = sp.current_user_top_tracks(limit=6)
    names = []
    pics = []
    artists = []
    previews = []
    for song in topSongs['items']:
        names.append(song['name'])
        previews.append(song['preview_url'])
        for artist in song['artists']:
            artists.append(artist['name'])
            break # this makes sure only the first artist is appended
        album_id = song['album']['id']
        album_info = sp.album(album_id)
        cover_art_url = album_info['images'][0]['url'] if len(album_info['images']) > 0 else None
        pics.append(cover_art_url)
    songData = zip(pics, names, artists, previews)
    
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

@app.route('/home')
def home():
    return render_template('home.html')

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
